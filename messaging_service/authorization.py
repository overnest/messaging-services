from pyramid.httpexceptions import HTTPUnauthorized

from messaging_service.models import User


def validate_user(request, query=False):
    try:
        user_id = request.jwt_claims['sub']

        if not query:
            return user_id
    except KeyError:
        raise HTTPUnauthorized

    user = request.dbsession.query(User).get(user_id)

    if user is None:
        raise HTTPUnauthorized

    return user
