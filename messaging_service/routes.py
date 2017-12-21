def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    config.add_static_view('uploads', 'messaging_service:static/uploads')

    # Users
    config.add_route('users', '/users')
    config.add_route('authorize', '/users/{username}/authorize')
    config.add_route('resend_verification_code', '/users/{username}/resendVerificationCode')
    config.add_route('verify_user', '/users/{username}/verify')

    # Friends
    config.add_route('friends', '/friends')
    config.add_route('respond_to_friend_request', '/friends/{username}')

    # Messages
    config.add_route('video_upload', '/messages/video/{upload_id}')
    config.add_route('create_video_message', '/messages/video')
    config.add_route('send_text_message', '/messages/text')
    config.add_route('messages', '/messages')
