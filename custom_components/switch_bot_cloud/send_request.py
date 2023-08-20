import base64
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
from http.client import HTTPSConnection
import yaml

SECRETS = None
BASE_URL = 'api.switch-bot.com'


def request(token, secret, path, data={}, method='GET'):
    # Switchbot authentication using secrets.yaml
    # token = SECRETS.get('switchbot_api_token')
    # secret =  SECRETS.get('switchbot_secret_key')
    nonce = uuid.uuid4()

    t = int(round(time.time() * 1000))
    string_to_sign = '{}{}{}'.format(token, t, nonce)

    string_to_sign = bytes(string_to_sign, 'utf-8')
    secret = bytes(secret, 'utf-8')

    sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

    encoded_data = json.dumps(data).encode('utf-8')
    headers = {
        "Authorization": str(token),
        "t": str(t),
        "sign": str(sign, 'utf-8'),
        "nonce": str(nonce),
        "Content-Type": "application/json; charset=utf8"
    }

    conn = HTTPSConnection(BASE_URL)
    conn.request(method, path, body=encoded_data, headers=headers)
    resp = conn.getresponse()
    data = resp.read()
    respStr = data.decode('utf-8')
    print(resp)
    print(respStr)
    response = json.loads(respStr)
    conn.close()

    if response['statusCode'] == 190:
        return response['message']
    elif response['statusCode'] == 100 and response['body']:
        return response['body']
    elif response['statusCode'] == 100:
        return response['message']
    else:
        return response
