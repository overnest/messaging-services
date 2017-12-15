from base64 import b64encode
import json

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
