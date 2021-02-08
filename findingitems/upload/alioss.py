import time
import json
import hmac
import base64
import datetime
from django.conf import settings
from hashlib import sha1 as sha


EXPIRE_TIME = 300


def get_iso_8601(expire):
    gmt = datetime.datetime.utcfromtimestamp(expire).isoformat()
    gmt += 'Z'
    return gmt


def get_token_by_dir(dir=''):
    now = int(time.time())
    expire_syncpoint = now + EXPIRE_TIME
    expire = get_iso_8601(expire_syncpoint)

    policy_dict = {}
    policy_dict['expiration'] = expire
    condition_array = []
    array_item = []
    array_item.append('starts-with')
    array_item.append('$key')
    array_item.append(dir)
    condition_array.append(array_item)
    # condition_array.append({'bucket': settings.ALIOSS_BUCKET_NAME})
    policy_dict['conditions'] = condition_array
    policy = json.dumps(policy_dict).strip()
    policy_encode = base64.b64encode(policy.encode())
    h = hmac.new(settings.ALIOSS_API_SECRET.encode(), policy_encode, sha)
    sign_result = base64.encodestring(h.digest()).strip()

    token_dict = {}
    token_dict['OSSAccessKeyId'] = settings.ALIOSS_API_ID
    token_dict['host'] = settings.ALIOSS_BUCKET_DOMAIN
    token_dict['policy'] = policy_encode.decode()
    token_dict['Signature'] = sign_result.decode()
    token_dict['expire'] = expire
    token_dict['dir'] = dir
    return token_dict
