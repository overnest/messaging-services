import json

import pyramid.httpexceptions as phe
from pyramid.response import Response
from pyramid.view import view_config
import qrcode
import qrcode.image.svg
from sqlalchemy import and_, or_

from ..models import (
    Friend,
    User,
    UserVerification,
)
from messaging_service.authorization import validate_user
from messaging_service.models.errors import (
    ExpiredVerificationCodeError,
    catch_duplicate_object_errors,
)


@view_config(route_name='users', renderer='json')
def users(request):
    users = request.dbsession.query(User).all()
    return {'users': [u.username for u in users]}


@view_config(route_name='user_detail', renderer='json')
def user_detail(request):
    request_user = request.dbsession.query(User).filter(
        User.username == request.matchdict['username']).first()

    token_user = validate_user(request, query=True)

    if not request_user:
        raise phe.HTTPNotFound

    if request_user.id != token_user.id:
        friendship = request.dbsession.query(Friend).filter(
            or_(
                and_(
                    Friend.target_id == request_user.id,
                    Friend.initiator_id == token_user.id,
                ),
                and_(
                    Friend.target_id == token_user.id,
                    Friend.initiator_id == request_user.id,
                )
            ),
            Friend.verified == True,  # noqa
        ).first()

        if not friendship:
            raise phe.HTTPNotFound

    # TODO right now this returns all information for the user. It will need to
    # be somewhat limited for friends.  (Omit mobile number, etc.)
    return {'user': request_user}


@view_config(route_name='users', request_method='POST')
def create_user(request):
    user = User.from_json(request.json_body)
    user.hash_password()

    verification = UserVerification(user)
    verification.hash_code()

    request.dbsession.add(user)
    request.dbsession.add(verification)

    with catch_duplicate_object_errors('user'):
        request.dbsession.flush()

    verification.send_code(request)

    return Response(status=201)


@view_config(route_name='authorize', request_method='POST')
def authorize_user(request):
    user = request.dbsession.query(User).filter(
        User.username == request.matchdict['username']).first()

    if not user.verify_password(request.body):
        return Response(status=401)

    if not user.verified:
        return Response(
            status=403,
            body=json.dumps({'message': "User not verified."}),
            charset="utf-8",
            content_type='application/json',
        )

    token = request.create_jwt_token(user.id)

    return Response(
        body=token,
        status=200,
        content_type="text/plain"
    )


@view_config(route_name='verify_user', request_method='POST')
def verify_user(request):
    user = request.dbsession.query(User).join(User.verifications).filter(
        User.username == request.matchdict['username']).first()

    if user is None:
        raise phe.HTTPNotFound

    valid_verification = None

    for verification in user.verifications:
        if verification.verify_code(request.body):
            valid_verification = verification

    if not valid_verification:
        raise phe.HTTPForbidden

    if valid_verification.expired:
        raise ExpiredVerificationCodeError(user.username)

    user.verified = True
    request.dbsession.add(user)

    return Response(status=204)


@view_config(route_name='resend_verification_code', request_method='POST')
def resend_verification_code(request):
    user = request.dbsession.query(User).filter(
        User.username == request.matchdict['username']).first()

    verification = UserVerification(user)
    verification.hash_code()

    request.dbsession.add(verification)
    request.dbsession.flush()

    verification.send_code(request)

    return Response(status=201)


@view_config(route_name='user_qr_code', request_method='GET')
def get_user_qr_code(request):
    token_user = validate_user(request, query=True)

    qr = qrcode.make(
        token_user.username,
        image_factory=qrcode.image.svg.SvgPathImage
    )

    return Response(
        status=200,
        body=str(qr),
        content_type='image/svg+xml',
    )
