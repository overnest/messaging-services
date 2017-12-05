import os.path
import shutil

from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import and_, or_

from ..models import (
    Friend,
    Message,
    Upload,
    User,
)
from ..tus import parse_metadata, tus_response


def _verify_target_is_friend(request, to_username):
    from_id = request.jwt_claims['sub']

    friend = request.dbsession.query(User).join(
        Friend,
        or_(
            and_(
                User.id == Friend.target_id,
                Friend.initiator_id == from_id,
                Friend.verified == True,
            ),
            and_(
                User.id == Friend.initiator_id,
                Friend.target_id == from_id,
                Friend.verified == True,
            )
        )
    ).filter(
        User.username == to_username
    ).first()

    return (from_id, friend)


@view_config(route_name='create_video_message', request_method='POST')
def create_video_message(request):
    """This endpoint implements the Tus creation service. A POST request
    creates a Message object as well as an Upload object and returns a Location
    to which additional PATCH requests may be sent in order to actually upload
    the file.
    """
    parsed_metadata = parse_metadata(request.headers)

    try:
        upload_length = int(request.headers['Upload-Length'])
    except:
        raise ValueError("Invalid or missing Upload-Length header.")

    current_user_id, friend = _verify_target_is_friend(
        request,
        parsed_metadata['to']
    )

    message = Message(
        from_id=current_user_id,
        to=friend,
        message_type='video',
    )

    upload = Upload(
        message=message,
        total_size=upload_length,
    )

    request.dbsession.add(message)
    request.dbsession.add(upload)
    request.dbsession.flush()

    location_url = request.route_url('append_to_upload', upload_id=upload.id)

    return tus_response(201, location=location_url)


@view_config(route_name='append_to_upload', request_method='HEAD')
def find_upload_offset(request):
    upload_id = int(request.matchdict['upload_id'])
    upload = request.dbsession.query(Upload).get(upload_id)

    return tus_response(200, upload_offset=upload.uploaded_size)


@view_config(route_name='append_to_upload', request_method='PATCH')
def append_to_upload(request):
    additional_size = int(request.headers['Content-Length'])
    offset_position = int(request.headers['Upload-Offset'])
    upload_id = int(request.matchdict['upload_id'])

    upload = request.dbsession.query(Upload).get(upload_id)

    if upload.uploaded_size != offset_position:
        return Response(status=409)

    partial_filename = os.path.join(
        request.registry.settings['uploads.temporary_directory'],
        "partial-upload.{upload_id}".format(upload_id=upload.id),
    )

    with open(partial_filename, 'ab') as partial_file:
        shutil.copyfileobj(request.body_file, partial_file)

    current_file_size = os.stat(partial_filename).st_size
    upload.uploaded_size = current_file_size

    if upload.uploaded_size >= upload.total_size:
        upload.complete = True

    request.dbsession.add(upload)

    return tus_response(204, upload_offset=upload.uploaded_size)


@view_config(route_name='send_text_message', request_method='POST')
def send_text_message(request):
    current_user_id, friend = _verify_target_is_friend(request, request.json_body['to'])

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
