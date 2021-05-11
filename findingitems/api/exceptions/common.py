from rest_framework.exceptions import APIException
from django.utils.translation import ugettext_lazy as _

from findingitems.api.exceptions import error_code as codes


class UnknownException(APIException):
    status_code = codes.UNKNOWN_CODE
    default_detail = _(codes.UNKNOWN_MSG)

    def __init__(self, msg=None):
        super(UnknownException, self).__init__(detail=msg)


class ParameterMissing(APIException):
    status_code = codes.MISS_REQUIRED_PARAMS_CODE
    default_detail = _(codes.MISS_REQUIRED_PARAMS_MSG)

    def __init__(self, msg=None):
        super(ParameterMissing, self).__init__(detail=msg)


class ParameterInvalid(APIException):
    status_code = codes.INVALID_PARAMS_CODE
    default_detail = _(codes.INVALID_PARAMS_MSG)

    def __init__(self, msg=None):
        super(ParameterInvalid, self).__init__(detail=msg)


class LoginFailedException(APIException):
    status_code = codes.LOGIN_FAILED_CODE
    default_detail = _(codes.LOGIN_FAILED_MSG)

    def __init__(self, msg=None):
        super(LoginFailedException, self).__init__(detail=msg)