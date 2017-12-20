import json

from pyramid.response import Response
from pyramid.view import view_config

from ..models import User, UserVerification


@view_config(route_name='users', renderer='json')
def users(request):
    users = request.dbsession.query(User).all()

    return {'users': users}


@view_config(route_name='users', request_method='POST')
def create_user(request):
    user = User.from_json(request.json_body)
    user.hash_password()
    request.dbsession.add(user)

    verification = UserVerification(user)
    verification.send_code(request)
    verification.hash_code()
    request.dbsession.add(verification)

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

    print(user)

    if user is None:
        return Response(status=404)

    valid = False

    for verification in user.verifications:
        if verification.verify_code(request.body):
            valid = True

    # TODO handle expiration

    if not valid:
        return Response(status=403)

    user.verified = True
    request.dbsession.add(user)

    return Response(status=204)
