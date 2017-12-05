from base64 import b64decode


class InvalidUploadMetadata(ValueError):
    def __init__(self, message):
        message = "Invalid Upload-Metadata specified. {}".format(message)
        super().__init__(message)


def parse_metadata(headers):
    raw_metadata = headers.get('Upload-Metadata', '').strip()

    # MUST be unique -- check

    if len(raw_metadata) == 0:
        return {}

    parsed_metadata = {}

    for pair in raw_metadata.split(','):
        try:
            key, raw_value = pair.split(" ")
        except ValueError:
            raise InvalidUploadMetadata("Is it a list of key-value pairs?")

        try:
            value = b64decode(raw_value).decode('utf-8')
            parsed_metadata[key] = value
        except:
            raise InvalidUploadMetadata("Are values provided in Base64?")

    return parsed_metadata
