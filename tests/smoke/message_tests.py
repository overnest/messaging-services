from base64 import b64encode
import json
from random import randint

from smoke.utilities import test, assertion


@test(requires={'friend'}, provides={'text_message'})
def send_message(context):
    response = context.post(
        'messages/text',
        data=json.dumps({
            'to': "alfred",
            'content': "hi, alfred",
        }),
        headers={'Authorization': context.authorization('betsy')}
    )
    response.raise_for_status()


@test(requires={'text_message'})
def retrieve_message(context):
    response = context.get(
        'messages',
        headers={'Authorization': context.authorization("alfred")}
    )
    response.raise_for_status()

    content = json.loads(response.content.decode())

    assertion(
        'One message is visible',
        lambda: len(content['messages']) == 1,
    )

    assertion(
        'The message is from Betsy',
        lambda: content['messages'][0]['from'] == 'betsy',
    )


@test(requires={'friend'}, provides={'upload_url'})
def create_video_upload(context):
    response = context.post(
        'messages/video',
        headers={
            'Authorization': context.authorization("betsy"),
            'Upload-Metadata': "to {}".format(
                b64encode('alfred'.encode('utf-8')).decode()),
            'Upload-Length': "20",
        },
    )
    response.raise_for_status()

    context.state['upload_url'] = response.headers['location']


@test(requires={'upload_url'}, provides={'completed_video'})
def upload_full_file(context):
    context.state['upload_data'] = str(randint(10000, 99999)) * 4

    response = context.patch(
        context.state['upload_url'],
        headers={
            'Authorization': context.authorization("betsy"),
            'Upload-Offset': "0",
        },
        data=context.state['upload_data']
    )
    response.raise_for_status()


@test(requires={'completed_video'}, provides={'signed_video_url'})
def retrieve_messages_including_video(context):
    response = context.get(
        'messages',
        headers={
            'Authorization': context.authorization("alfred"),
        }
    )
    response.raise_for_status()

    body = json.loads(response.content.decode())

    video_message = None

    for message in body['messages']:
        if message['type'] == 'video':
            video_message = message

    assertion(
        'The video message is present',
        lambda: video_message is not None
    )

    assertion(
        'The content link is present',
        lambda: bool(video_message.get('contentLink'))
    )

    context.state['signed_video_url'] = video_message['contentLink']


@test(requires={'signed_video_url'})
def download_video_content(context):
    response = context.get(
        context.state['signed_video_url']
    )
    response.raise_for_status()

    assertion(
        'The "video" is the same as the one we uploaded.',
        lambda: response.content.decode() == context.state['upload_data']
    )
