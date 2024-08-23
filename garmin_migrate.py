import logging
import os
from gsync import GSync
from gauth import GAuth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GARMIN_DST_USER = os.environ.get('GARMIN_DST_USER')
GARMIN_DST_PASSWORD = os.environ.get('GARMIN_DST_PASSWORD')
if os.environ.get('GARMIN_DST_IS_CN') is not None:
    GARMIN_DST_IS_CN = bool(os.environ.get('GARMIN_DST_IS_CN'))
else:
    GARMIN_DST_IS_CN = False
GARMIN_DST_TOKEN_STORE = os.environ.get('GARMIN_DST_TOKEN_STORE')
GARMIN_SRC_USER = os.environ.get('GARMIN_SRC_USER')
GARMIN_SRC_PASSWORD = os.environ.get('GARMIN_SRC_PASSWORD')
if os.environ.get('GARMIN_SRC_IS_CN') is not None:
    GARMIN_SRC_IS_CN = bool(os.environ.get('GARMIN_SRC_IS_CN'))
else:
    GARMIN_SRC_IS_CN = False
GARMIN_SRC_TOKEN_STORE = os.environ.get('GARMIN_SRC_TOKEN_STORE')
if os.environ.get('GARMIN_SYNC_NUM') is not None:
    GARMIN_SYNC_NUM = int(os.environ.get('GARMIN_SYNC_NUM'))
else:
    GARMIN_SYNC_NUM = 10

if GARMIN_DST_USER is None:
    raise Exception('GARMIN_DST_USER is None')
if GARMIN_DST_PASSWORD is None:
    raise Exception('GARMIN_DST_PASSWORD is None')
if GARMIN_SRC_USER is None:
    raise Exception('GARMIN_SRC_USER is None')
if GARMIN_SRC_PASSWORD is None:
    raise Exception('GARMIN_SRC_PASSWORD is None')

GARMIN_DST_TOKEN_FILE = "garmin_dst_token.txt"
GARMIN_SRC_TOKEN_FILE = "garmin_src_token.txt"

gauth_src = GAuth(GARMIN_SRC_TOKEN_STORE, GARMIN_SRC_USER, GARMIN_SRC_PASSWORD, GARMIN_SRC_IS_CN, GARMIN_SRC_TOKEN_FILE)
gauth_src.login()
garmin_src = gauth_src.garmin

gauth_dst = GAuth(GARMIN_DST_TOKEN_STORE, GARMIN_DST_USER, GARMIN_DST_PASSWORD, GARMIN_DST_IS_CN, GARMIN_DST_TOKEN_FILE)
gauth_dst.login()
garmin_dst = gauth_dst.garmin

profile_src = garmin_src.get_user_profile()
logger.info(f"源账号信息。{profile_src}")
profile_dst = garmin_dst.get_user_profile()
logger.info(f"目标账号信息。{profile_dst}")

sync = GSync(garmin_src, garmin_dst, GARMIN_SYNC_NUM)
sync.migrate()

sync = GSync(garmin_dst, garmin_src, GARMIN_SYNC_NUM)
sync.migrate()
