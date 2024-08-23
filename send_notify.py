import os
import requests

PUSH_PLUS_TOKEN = os.environ.get('PUSH_PLUS_TOKEN')


def send_push(msg):
    send_push_plus(msg)


def send_push_plus(msg):
    if PUSH_PLUS_TOKEN is not None:
        url = 'http://www.pushplus.plus/send'
        data = {
            "token": PUSH_PLUS_TOKEN,
            "title": "Garmin账号同步",
            "content": msg
        }
        requests.post(url, data=data)
