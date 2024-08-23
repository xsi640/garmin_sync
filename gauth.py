import logging
from send_notify import send_push

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GAuth:
    def __init__(self, token, username, password, is_cn, file_name):
        self.token = token
        self.username = username
        self.password = password
        self.is_cn = is_cn
        self.file_name = file_name
        self.garmin = None

    def read_token_by_file(self):
        try:
            with open(self.file_name, 'r') as file:
                self.token = file.read()
        except FileNotFoundError as e:
            logger.info(f"File not found: {self.file_name}")
            raise e
        except Exception as e:
            logger.info(f"Error reading file: {e}")
            raise e

    def write_token_by_file(self):
        if self.token is None:
            return
        try:
            with open(self.file_name, 'w') as file:
                file.write(self.token)
        except Exception as e:
            logger.info(f"Error writing to file: {e}")
            raise e

    def login_account(self):
        try:
            garmin = Garmin(email=self.username, password=self.password, is_cn=self.is_cn)
            garmin.login()
            self.token = garmin.garth.dumps()
            self.garmin = garmin
            self.write_token_by_file()
        except GarminConnectAuthenticationError as e:
            raise Exception(f"Authentication error: {e}")
        except Exception as e:
            raise Exception(f"Error logging in: {e}")

    def check_token(self):
        try:
            garmin = Garmin()
            garmin.login(self.token)
            self.garmin = garmin
        except Exception as e:
            logger.info(f"Error checking token: {e}")
            send_push(f"缓存账号过期，请更新。username: {self.username}")
            raise e

    def login(self):
        try:
            if self.token is not None:
                logger.info("验证登录，验证缓存中的token。")
                self.check_token()
            if self.garmin is None:
                logger.info("验证登录，读取文件中的token。")
                self.read_token_by_file()
                self.check_token()
            if self.garmin is None:
                logger.info("验证登录，重新登录。")
                self.login_account()
            if self.garmin is None:
                logger.info("验证登录，失败。")
                raise Exception("token config error")
        except Exception as e:
            raise Exception(f"Error logging in: {e}")
