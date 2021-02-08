import jwt
from django.conf import settings

import datetime
import logging

logger = logging.getLogger('django.jwt.utils')


def encrypt_token(payload, expire=settings.JWT_EXPIRE_DURATION, is_expire=True):
    if is_expire:
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=expire)
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')
    return token


def decrypt_token(token):
    print('decrypt {0}'.format(token))
    payload = {}
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms='HS256')
    except Exception as e:
        print(str(e))
        logger.debug('Decode %s failed: %s' % (token, str(e)))

    print(payload)
    return payload

