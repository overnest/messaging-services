from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import and_, or_

from ..models import Friend
from ..models import User
from ..models import Message


@view_config(route_name='send_text_message', request_method='POST')
def send_text_message(request):
    current_user_id = request.jwt_claims['sub']

    # Verify target is a friend
    target_username = request.json_body['to']

    friend = request.dbsession.query(User).join(
        Friend,
        or_(
            and_(
                User.id == Friend.target_id,
                Friend.initiator_id == current_user_id,
                Friend.verified == True,
            ),
            and_(
                User.id == Friend.initiator_id,
                Friend.target_id == current_user_id,
                Friend.verified == True,
            )
        )
    ).filter(
        User.username == target_username
    ).first()

    # Create message
    message = Message(
        from_id=current_user_id,
        to=friend,
        message_type='text',
        content=request.json_body['content']
    )
    request.dbsession.add(message)

    return Response(status=201)


@view_config(route_name='messages', request_method='GET', renderer='json')
def messages(request):
    current_user_id = request.jwt_claims['sub']

    messages = request.dbsession.query(Message).filter(
        Message.to_id == current_user_id,
        Message.read == False,
    ).all()

    return {"messages": messages}
