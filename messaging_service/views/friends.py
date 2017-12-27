import pyramid.httpexceptions as phe
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import and_, or_

from messaging_service.models.errors import DuplicateObjectError
from ..authorization import validate_user
from ..models import Friend
from ..models import User


@view_config(route_name='friends', request_method='GET', renderer='json')
def friends(request):
    current_user_id = validate_user(request)

    confirmed_friends = request.dbsession.query(User).join(
        Friend,
        or_(
            and_(
                User.id == Friend.initiator_id,
                Friend.initiator_id != current_user_id
            ),
            and_(
                User.id == Friend.target_id,
                Friend.target_id != current_user_id
            )
        )
    ).filter(
        or_(
            Friend.initiator_id == current_user_id,
            Friend.target_id == current_user_id,
        ),
        Friend.verified,
    ).all()

    outbound_requests = request.dbsession.query(User).join(
        Friend,
        User.id == Friend.target_id,
    ).filter(
        Friend.initiator_id == current_user_id,
        Friend.verified != True
    ).all()

    inbound_requests = request.dbsession.query(User).join(
        Friend,
        User.id == Friend.initiator_id,
    ).filter(
        Friend.target_id == current_user_id,
        Friend.verified != True
    ).all()

    return {
        'friends': [f.username for f in confirmed_friends],
        'friendRequests': {
            'outbound': [f.username for f in outbound_requests],
            'inbound': [f.username for f in inbound_requests],
        }
    }


@view_config(route_name='friends', request_method='POST', renderer='json')
def create_friend(request):
    initiator = validate_user(request, query=True)

    target = request.dbsession.query(User).filter(
        User.username == request.json_body['username']).first()

    if target is None:
        raise phe.HTTPNotFound

    if target.id == initiator.id:
        raise phe.HTTPBadRequest("Cannot issue a friend request to yourself.")

    previous_friend_requests = request.dbsession.query(Friend).filter(
        or_(
            and_(
                Friend.initiator_id == initiator.id,
                Friend.target_id == target.id,
            ),
            and_(
                Friend.target_id == initiator.id,
                Friend.initiator_id == target.id,
            ),
        )
    ).all()

    friend_request_to_save = None

    for friend_request in previous_friend_requests:
        if friend_request.verified:
            # Friendship exists and is verified.
            return Response(status=204)
        elif friend_request.target_id == initiator.id:
            # Reciprocal friend request exists; verify it.
            friend_request.verified = True
            friend_request_to_save = friend_request
            break
        else:
            raise DuplicateObjectError("friend request")

    if friend_request_to_save is None:
        friend_request_to_save = Friend(
            initiator=initiator,
            target=target,
        )

    request.dbsession.add(friend_request_to_save)
    return Response(status=202)


@view_config(route_name='respond_to_friend_request', request_method='POST')
def confirm_friend(request):
    friend_request = (
        request.dbsession.query(Friend).join(
            User,
            User.id == Friend.initiator_id,
        ).filter(
            User.username == request.matchdict['username'],
            Friend.target_id == validate_user(request)
        ).first()
    )

    if friend_request is None:
        return Response(status=404)

    friend_request.verified = True
    request.dbsession.add(friend_request)

    return Response(status=201)


@view_config(route_name='respond_to_friend_request', request_method='DELETE')
def delete_friend(request):
    friend_request = (
        request.dbsession.query(Friend).join(
            User,
            User.id == Friend.initiator_id
        ).filter(
            User.username == request.matchdict['username'],
            Friend.target_id == validate_user(request)
        ).first()
    )

    request.dbsession.delete(friend_request)

    return Response(status=204)

