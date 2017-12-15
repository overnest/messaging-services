from smoke.setup import context
import smoke.user_tests as user_tests
import smoke.message_tests as message_tests

TESTS = [
    user_tests.create_users,
    user_tests.authorize_users,
    user_tests.send_friend_request,
    user_tests.accept_friend_request,
    message_tests.send_message,
    message_tests.retrieve_message,
    message_tests.create_video_upload,
]

for test in TESTS:
    test(context)
