from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import datetime
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import transaction

from findingitems.api.exceptions.common import (
    ParameterInvalid,
    LoginFailedException,
    UnknownException,
)
from findingitems.api.exceptions import error_msg
from findingitems.wechat.utils import *
import findingitems.jwt.utils as jwt_utils

from findingitems.users.models import (
    AuthUser,
    UserSettings
)

from findingitems.location.models import (
    Location,
    LocationMemberShip,
)

from .serializers import (
    UserLoginSerializer
)

from .permissions import IsUserAuthenticated

from findingitems.upload.alioss import get_token_by_dir


import logging

logger = logging.getLogger('django.api.views')


class WechatLoginView(APIView):

    def get_wechat_gender(self, gender):
        if gender is None or int(gender) == 0:
            return None

        return int(gender) - 1

    def post(self, request, format=None):
        js_code = request.data.get('js_code', None)
        encryptedData = request.data.get('encryptedData', None)
        iv = request.data.get('iv', None)

        if js_code is None:
            logger.debug('Wechat Login: js_code is null')
            raise ParameterInvalid(error_msg.JS_CODE_REQUIRED)

        wechat_c2s_result = verify_wechat_user(js_code)
        if not wechat_c2s_result:
            logger.debug('Wechat Login: code2session fail. js_code: %s' % js_code)
            raise LoginFailedException(error_msg.WECHAT_LOGIN_FAIL)

        wechat_openid = wechat_c2s_result.get('openid', '')
        if wechat_openid == '':
            logger.debug('Wechat Login: openid is null. js_code: %s' % js_code)
            raise LoginFailedException(error_msg.WECHAT_LOGIN_FAIL)

        wechat_user_info = {}
        logger.debug('Wechat Login: session_key is %s' % wechat_c2s_result.get('session_key', ''))
        try:
            wechat_user_info = decrypted_wechat_user_info(encryptedData, iv, wechat_c2s_result.get('session_key', ''))
        except Exception as e:
            logger.error('Wechat Login: get wechat user info error %s' % str(e))

        real_name = wechat_user_info.get('nickName', None)
        avatar_url = wechat_user_info.get('avatarUrl', None)

        try:
            user = AuthUser.objects.get(username=wechat_openid, wechat_openid=wechat_openid)
            user.real_name = real_name

            if user.avatar_url is None or user.avatar_url == '':
                user.avatar_url = avatar_url

            user.save()
        except ObjectDoesNotExist:
            try:
                with transaction.atomic():
                    user = AuthUser()
                    user.username = wechat_openid
                    user.wechat_openid = wechat_openid
                    wechat_unionid = wechat_c2s_result.get('unionid', '')
                    if wechat_unionid == '':
                        wechat_unionid = gen_fake_wechat_unionid()
                    user.wechat_unionid = wechat_unionid
                    user.avatar_url = avatar_url
                    user.real_name = real_name
                    user.date_joined = datetime.datetime.now()
                    user.save()

                    loc = Location.objects.create(
                        owner=user,
                        name=settings.DEFAULT_LOCATION_NAME,
                    )
                    loc.save()

                    profile = UserSettings.objects.create(
                        user=user,
                        default_loc=loc
                    )
                    profile.save()

                    lms = LocationMemberShip.objects.create(
                        member=user,
                        location=loc,
                        role=LocationMemberShip.LOCATION_MEMBER_ROLE_OWNER,
                        alias_name=loc.name,
                    )
                    lms.save()

            except Exception as e:
                print(str(e))
                logger.debug('Wechat Login: create user with openid %s failed. %s' % (wechat_openid, str(e)))
                raise UnknownException(error_msg.WECHAT_USER_CREATION_FAILED)

        except Exception as e:
            logger.error('Wechat Login: exception %s' % str(e))
            raise UnknownException(error_msg.WECHAT_LOGIN_EXCEPTION)

        payload = {
            'user_id': user.id
        }
        token = jwt_utils.encrypt_token(
            payload,
        )
        serializer = UserLoginSerializer(user)
        res_data = serializer.data
        res_data['token'] = token
        res_obj = Response({'code': 0,
                            'error_msg': '',
                            'data': res_data
                           },
                           status=status.HTTP_200_OK)

        return res_obj


class UserCheckAuthView(APIView):
    permission_classes = [IsUserAuthenticated, ]

    def post(self, request):
        res_data = {}
        payload = {
            'user_id': request.user.id
        }
        token = jwt_utils.encrypt_token(
            payload,
        )
        serializer = UserLoginSerializer(request.user)
        res_data = serializer.data
        res_data['token'] = token
        res_obj = Response({'code': 0,
                            'error_msg': '',
                            'data': res_data
                            },
                            status=status.HTTP_200_OK)
        return res_obj


class OssTokenView(APIView):
    permission_classes = [IsUserAuthenticated, ]

    def get(self, request, *args, **kwargs):
        token_dict = get_token_by_dir(dir=settings.ALIOSS_INSTRUCTION_DIR)
        return Response({'code': 0, 'error_msg': '', 'data': token_dict})
