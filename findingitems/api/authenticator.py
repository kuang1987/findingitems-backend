from rest_framework.authentication import BaseAuthentication
from findingitems.users.models import AuthUser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from rest_framework import HTTP_HEADER_ENCODING

import findingitems.jwt.utils as jwt_utils
import re


class UserJWTAuthentication(BaseAuthentication):
    www_authenticate_realm = 'api'

    def get_user(self, payload={}):
        user_id = payload.get('user_id', -1)
        try:
            user = AuthUser.objects.get(id=user_id)
        except ObjectDoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return user

    def authenticate(self, request):
        print('user token')
        token = self.get_token(request)
        if token is None:
            return None, None
            # raise exceptions.AuthenticationFailed('No token')

        payload = {}
        try:
            print(token)
            payload = jwt_utils.decrypt_token(token)
        except Exception:
            return None, None
            # raise exceptions.AuthenticationFailed('Invalid token')
        user = self.get_user(payload=payload)
        if user is None:
            return None, None

        print(user)
        print(payload)

        return user, payload

    def get_token(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token is None:
            return token

        if re.match("^b\'", token):
            token = re.sub("^b\'", "", token)
            token = re.sub("\'$", "", token)

        token = re.sub('^Bearer', "", token)
        token = token.strip()

        if token == '':
            return None

        if isinstance(token, str):
            # Work around django test client oddness
            token = token.encode(HTTP_HEADER_ENCODING)

        return token
