from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError


class DuplicateObjectError(Exception):
    def __init__(self, object_type='object'):
        super().__init__("Invalid request; duplicate {}".format(object_type))


class ExpiredVerificationCodeError(Exception):
    def __init__(self, user):
        self.user = user
        super().__init__("Invalid request; code for {} has expired.".format(user))


@contextmanager
def catch_duplicate_object_errors(object_type):
    try:
        yield
    except IntegrityError:
        raise DuplicateObjectError(object_type)

