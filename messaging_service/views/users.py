from pyramid.response import Response
from pyramid.view import view_config

from ..models import User


@view_config(route_name='users', renderer='json')
def users(request):
    users = request.dbsession.query(User).all()

    return {'users': users}


@view_config(route_name='users', request_method='POST')
def create_user(request):
    user = User.from_json(request.json_body)
    user.hash_password()
    request.dbsession.add(user)

    return Response(status=201)


@view_config(route_name='authorize', request_method='POST')
def authorize_user(request):
    user = request.dbsession.query(User).filter(
        User.username == request.matchdict['username']).first()

    if not user.verify_password(request.body):
        return Response(status=401)

    token = request.create_jwt_token(user.id)

    return Response(
        body=token,
        status=200,
        content_type="text/plain"
    )
