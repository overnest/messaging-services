import json

import pyramid.httpexceptions as phe
from pyramid.response import Response
from pyramid.view import exception_view_config

from messaging_service.serialization import (
    DeserializationError,
)
from messaging_service.models.errors import (
    DuplicateObjectError,
    ExpiredVerificationCodeError,
)


@exception_view_config(DeserializationError)
def deserialization_error(exc, request):
    return Response(
        body=json.dumps({'message': str(exc)}),
        charset="utf-8",
        content_type="application/json",
        status=400,
    )


@exception_view_config(DuplicateObjectError)
def duplicate_entity_error(exc, request):
    return Response(
        body=json.dumps({'message': str(exc)}),
        charset="utf-8",
        content_type="application/json",
        status=409,
    )


@exception_view_config(phe.HTTPInternalServerError)
def internal_server_error(exc, request):
    return Response(
        body=json.dumps({'message': "Internal Server Error"}),
        charset="utf-8",
        content_type="application/json",
        status=500,
    )


@exception_view_config(phe.HTTPNotFound)
def not_found_error(exc, request):
    return Response(
        body=json.dumps({'message': "Route or entity not found"}),
        charset="utf-8",
        content_type="application/json",
        status=404,
    )


@exception_view_config(ExpiredVerificationCodeError)
def expired_verification_error(exc, request):
    return Response(
        body=json.dumps({
            'message': str(exc),
            'resendLink': request.route_url(
                'resend_verification_code',
                username=request.matchdict['username'],
            )
        }),
        charset="utf-8",
        content_type="application/json",
        status=400,
    )
