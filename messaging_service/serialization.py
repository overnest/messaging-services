class DeserializationError(ValueError):
    """General errors occurring during the validation and processing of
    incoming JSON requests.
    """
    def __init__(self, message):
        super().__init__(message)


class MissingFieldsError(DeserializationError):
    """Errors resulting from required fields being omitted or empty in JSON."""
    def __init__(self, cls, *fields):
        class_name = cls.__name__.lower()
        message = "Invalid {} payload: missing required field(s): {}".format(
            class_name,
            ', '.join(fields),
        )
        super().__init__(message)
