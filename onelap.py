import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OneLap:

    def __init__(self, token):
        self.token = token

    def check_token(self):
        try:
            r = requests.get("https://www.onelap.cn/api/userinfo", headers={"Authorization": f"{self.token}"})
            logger.info(r.json())
        except Exception as e:
            raise Exception(f"Error checking token: {e}")

    def get_activities(self):
        pass


ol = OneLap("eyJpc3MiOjYwNTUxLCJuYmYiOjE3MjQ2MzYzNTEsImV4cCI6MTcyNDgwOTIxMSwibW9iaWxlIjoiMTM2OTEyNjI4NTMiLCJuaWNrbmFtZSI6Ilx1NWUxNVx1NWUxNSJ9.e1h07FdQYGwW7OteKehVSD4k5xI=")
ol.check_token()