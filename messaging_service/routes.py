def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    # Users
    config.add_route('users', '/users')
    config.add_route('authorize', '/users/{username}/authorize')

    # Friends
    config.add_route('friends', '/friends')
    config.add_route('respond_to_friend_request', '/friends/{username}')

    # Messages
    config.add_route('send_text_message', '/messages/text')
    config.add_route('messages', '/messages')
