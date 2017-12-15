import json

from smoke.utilities import test


@test(provides={'users'})
def create_users(context):
    context.state['users'] = {
        'alfred': {
            'username': "alfred",
            'email': "alf@example.com",
            'password': "foo",
        },
        'betsy': {
            'username': "betsy",
            'email': "betsy@example.com",
            'password': "bar",
        },
        'charles': {
            'username': "charles",
            'email': "charles@example.com",
            'password': "baz",
        }
    }

    for _, data in context.state['users'].items():
        response = context.post('users', data=json.dumps(data))
        response.raise_for_status()


@test(provides={'tokens'}, requires={'users'})
def authorize_users(context):
    for username, data in context.state['users'].items():
        response = context.post(
            'users/{}/authorize'.format(username),
            data=data['password'],
        )
        response.raise_for_status()
        data['token'] = response.content.decode()


@test(provides={'friend_request'}, requires={'tokens'})
def send_friend_request(context):
    response = context.post(
        'friends',
        data=json.dumps({'username': "betsy"}),
        headers={'Authorization': context.authorization('alfred')},
    )
    response.raise_for_status()


# TODO: Test for GET friends.


@test(provides={'friend'}, requires={'friend_request'})
def accept_friend_request(context):
    response = context.post(
        'friends/alfred',
        headers={'Authorization': context.authorization('betsy')},
    )
    response.raise_for_status()
