import datetime
import logging
import os
import sys
import zipfile
import requests

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
)

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
GARMIN_SRC_TOKEN_STORE = os.environ.get('GARMIN_SRC_TOKEN_STORE')
if os.environ.get('GARMIN_SRC_IS_CN') is not None:
    GARMIN_SRC_IS_CN = bool(os.environ.get('GARMIN_SRC_IS_CN'))
else:
    GARMIN_SRC_IS_CN = False
if os.environ.get('GARMIN_SYNC_NUM') is not None:
    GARMIN_SYNC_NUM = int(os.environ.get('GARMIN_SYNC_NUM'))
else:
    GARMIN_SYNC_NUM = 10
GARMIN_ACTIVITY_DOWNLOAD_PATH = "activities"
PUSH_PLUS_TOKEN = os.environ.get('PUSH_PLUS_TOKEN')

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


def read_file_contents(file_path):
    try:
        with open(file_path, 'r') as file:
            contents = file.read()
            return contents
    except FileNotFoundError:
        logger.info(f"File not found: {file_path}")
        return None
    except Exception as e:
        logger.info(f"Error reading file: {e}")
        return None


def write_to_file(file_path, contents):
    try:
        with open(file_path, 'w') as file:
            file.write(contents)
    except Exception as e:
        logger.info(f"Error writing to file: {e}")


def send_push_plus(msg):
    if PUSH_PLUS_TOKEN is not None:
        url = 'http://www.pushplus.plus/send'
        data = {
            "token": PUSH_PLUS_TOKEN,
            "title": "Garmin账号同步",
            "content": msg
        }
        requests.post(url, data=data)


def login(username, password, is_cn):
    try:
        garmin = Garmin(email=username, password=password, is_cn=is_cn)
        garmin.login()
        return garmin
    except GarminConnectAuthenticationError as e:
        raise Exception(f"Authentication error: {e}")
    except Exception as e:
        raise Exception(f"Error logging in: {e}")


def check_token(token):
    try:
        garmin = Garmin()
        garmin.login(token)
        return garmin
    except Exception as e:
        logger.info(f"Error checking token: {e}")
        return None


def get_garmin_connect(src: bool):
    logger.info(f"{'源' if src else '目标'}账号，验证缓存中的token。")
    garmin_connect = None
    try:
        if src:
            if GARMIN_SRC_TOKEN_STORE is not None:
                logger.info("源账号，验证缓存中的token。")
                garmin_connect = check_token(GARMIN_SRC_TOKEN_STORE)
        else:
            if GARMIN_DST_TOKEN_STORE is not None:
                logger.info("目标账号，验证缓存中的token。")
                garmin_connect = check_token(GARMIN_DST_TOKEN_STORE)
    except Exception as e:
        logger.info(f"Error checking token: {e}")
        send_push_plus(f"{'源' if src else '目标'}账号缓存token过期，请更新。")
        garmin_connect = None
    if garmin_connect is not None:
        return garmin_connect
    try:
        if src:
            logger.info("源账号，验证本地文件中的token。")
            garmin_connect = check_token(read_file_contents(GARMIN_SRC_TOKEN_FILE))
        else:
            logger.info("目标账号，验证本地文件中的token。")
            garmin_connect = check_token(read_file_contents(GARMIN_DST_TOKEN_FILE))
    except Exception as e:
        logger.info(f"Error checking token: {e}")
        garmin_connect = None
    if garmin_connect is not None:
        return garmin_connect
    try:
        if src:
            logger.info("源账号，登录并写入本地文件。")
            garmin_connect = login(GARMIN_SRC_USER, GARMIN_SRC_PASSWORD, GARMIN_SRC_IS_CN)
            write_to_file(GARMIN_SRC_TOKEN_FILE, garmin_connect.garth.dumps())
        else:
            logger.info("目标账号，登录并写入本地文件。")
            garmin_connect = login(GARMIN_DST_USER, GARMIN_DST_PASSWORD, GARMIN_DST_IS_CN)
            write_to_file(GARMIN_DST_TOKEN_FILE, garmin_connect.garth.dumps())
    except Exception as e:
        logger.info(f"Error logging in: {e}")
        send_push_plus(f"{'源' if src else '目标'}账号登录失败。")
        garmin_connect = None
    return garmin_connect


garmin_src = get_garmin_connect(True)
if garmin_src is None:
    raise Exception("源账号登录失败")

garmin_dst = get_garmin_connect(False)
if garmin_dst is None:
    raise Exception("目标账号登录失败")

activities_dst_cache = []
query_for_date = []


def exists_activity(src_activity_start_time):
    logger.info(f"根据活动时间判断是否需要上传。{src_activity_start_time}")
    for_date = src_activity_start_time[:10]
    is_query_for_date = for_date in query_for_date
    if not is_query_for_date:
        logger.info("日期不在查询日期内，新查询。")
        end_date = datetime.datetime.strptime(for_date, '%Y-%m-%d')
        date_list = [(end_date - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        for date in date_list:
            query_for_date.append(date)

        for activity_dst in garmin_dst.get_activities_by_date(startdate=date_list[-1], enddate=for_date):
            activities_dst_cache.append(activity_dst)

    for activity in activities_dst_cache:
        if activity["startTimeLocal"] == src_activity_start_time:
            logger.info("活动已存在，无需上传。")
            return True

    return False


def sync_activity(src_activity_id):
    if not os.path.exists(GARMIN_ACTIVITY_DOWNLOAD_PATH):
        os.mkdir(GARMIN_ACTIVITY_DOWNLOAD_PATH)
    data = garmin_src.download_activity(src_activity_id, dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL)
    logger.info(f"从源服务器下载活动 id:{src_activity_id}")
    output_file = f"{GARMIN_ACTIVITY_DOWNLOAD_PATH}/{src_activity_id}.zip"
    if os.path.exists(output_file):
        os.remove(output_file)
    with open(output_file, 'wb') as fb:
        fb.write(data)

    extract_path = f"{GARMIN_ACTIVITY_DOWNLOAD_PATH}/{src_activity_id}_tmp"
    if not os.path.exists(extract_path):
        os.mkdir(extract_path)
    with zipfile.ZipFile(output_file, 'r') as zip:
        zip.extractall(extract_path)
    os.remove(output_file)
    for f in os.listdir(extract_path):
        path = os.path.join(extract_path, f)
        garmin_dst.upload_activity(path)
        logger.info(f"上传到目标服务器. file:{path}")
        os.remove(path)
    os.rmdir(extract_path)


activities_src = garmin_src.get_activities(0, 1)
activities_dst = garmin_dst.get_activities(0, 1)
logger.info(activities_src[0])
logger.info(activities_dst[0])
last_activity_start_time_src = activities_src[0]["startTimeLocal"]
last_activity_start_time_dst = activities_dst[0]["startTimeLocal"]

if last_activity_start_time_dst == last_activity_start_time_dst:
    logger.info("最新两个账号最新的活动时间相同，无需同步。")
else:
    start = 0
    limit = GARMIN_SYNC_NUM
    sync_activity_count = 0
    while True:
        activities_src = garmin_src.get_activities(start, limit)
        logger.info(f"下载国际账号的活动。start:{start}, limit:{limit}")
        if len(activities_src) == 0:
            logger.info("没有更多活动。结束。")
            break

        for activity_src in activities_src:
            activity_id = activity_src.get("activityId")
            start_time_local = activity_src.get("startTimeLocal")
            if exists_activity(start_time_local):
                logger.info("活动已存在，无需上传。结束同步。")
                sys.exit(0)
            else:
                sync_activity(activity_id)
                sync_activity_count += 1

        if len(activities_src) < limit:
            logger.info("没有更多活动。结束。")
            break
        start += limit
    send_push_plus(f"共同步 {sync_activity_count} 个活动。")
