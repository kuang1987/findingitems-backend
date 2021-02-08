from rest_framework import exceptions
from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import set_rollback


def api_exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.
s
    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        # if isinstance(exc.detail, (list, dict)):
        #     err_data = exc.detail
        # else:
        #     err_data = {'detail': exc.detail}
        err_data = exc.detail

        set_rollback()
        data = {}
        data['code'] = exc.status_code
        data['error_msg'] = str(err_data) if isinstance(err_data, str) else err_data
        data['data'] = {}
        return Response(data, status=200, headers=headers)

    return None
