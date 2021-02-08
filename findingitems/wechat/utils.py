import requests

from django.conf import settings
import base64
import json
from Crypto.Cipher import AES
import uuid

import logging

logger = logging.getLogger('django.api.wechat')


class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)
        payload = self._unpad(cipher.decrypt(encryptedData))
        decrypted = json.loads(payload)

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


def decrypted_wechat_user_info(data, iv, session_key):
    appId = settings.F_ITEMS_WECHAT_APP_ID
    encrypted_data = data
    iv = iv

    pc = WXBizDataCrypt(appId, session_key)

    return pc.decrypt(encrypted_data, iv)


def verify_wechat_user(js_code):
    params = {
        'appid': settings.F_ITEMS_WECHAT_APP_ID,
        'secret': settings.F_ITEMS_WECHAT_APP_SECRET,
        'js_code': js_code,
        'grant_type': 'authorization_code',
    }

    code2session_endpoint = '%s/sns/jscode2session' % settings.WECHAT_API_ENDPOINT
    try:
        r = requests.get(code2session_endpoint, params=params)
        if r and r.status_code == 200:
            payload = r.json()
            logger.debug('code2session error: %s' % payload)

            errcode = payload.get('errcode', -1)
            errmsg = payload.get('errmsg', 'error')
            openid = payload.get('openid', '')
            session_key = payload.get('session_key', '')
            unionid = payload.get('unionid', '')
            if errcode != 0:
                if openid != '' and session_key != '':
                    return {
                        'openid': openid,
                        'unionid': unionid,
                        'session_key': session_key,
                    }
                logger.debug('code2session exists: errcode - %s, errmsg - %s' % (errcode, errmsg))
                return {}

            if openid == '':
                logger.debug('code2session error: openid is null')
                return {}

            if session_key == '':
                logger.debug('code2session error: session_key is null')
                return {}

            return {
                'openid': openid,
                'unionid': unionid,
                'session_key': session_key,
            }

        logger.debug('code2session error: %d %s' % (r.status_code, r.content))
    except requests.Timeout:
        logger.debug('code2session error: timeout')
    except Exception as e:
        logger.debug('code2session error: %s' % str(e))

    return {}


def gen_fake_wechat_unionid():
    return "fake:%s" % str(uuid.uuid4())


if __name__ == '__main__':
    import django
    django.setup()
    verify_wechat_user('07152mqV0aOdW12XcYqV02AdqV052mqP')
