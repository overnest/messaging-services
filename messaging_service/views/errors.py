import json

from pyramid.response import Response
from pyramid.view import exception_view_config

from messaging_service.serialization import (
    DeserializationError
)


@exception_view_config(DeserializationError)
def deserialization_error(exc, request):
    return Response(
        body=json.dumps({
            'message': str(exc)
        }),
        charset="utf-8",
        content_type="application/json",
        status=400,
    )
