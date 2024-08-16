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

GARMIN_GLOBAL_USER = os.environ.get('GARMIN_GLOBAL_USER')
GARMIN_GLOBAL_PASSWORD = os.environ.get('GARMIN_GLOBAL_PASSWORD')
GARMIN_GLOBAL_TOKEN_STORE = os.environ.get('GARMIN_GLOBAL_TOKEN_STORE')
GARMIN_CN_USER = os.environ.get('GARMIN_CN_USER')
GARMIN_CN_PASSWORD = os.environ.get('GARMIN_CN_PASSWORD')
GARMIN_CN_TOKEN_STORE = os.environ.get('GARMIN_CN_TOKEN_STORE')
if os.environ.get('GARMIN_SYNC_NUM') is not None:
    GARMIN_SYNC_NUM = int(os.environ.get('GARMIN_SYNC_NUM'))
else:
    GARMIN_SYNC_NUM = 10
GARMIN_ACTIVITY_DOWNLOAD_PATH = "activities"
PUSH_PLUS_TOKEN = os.environ.get('PUSH_PLUS_TOKEN')

if GARMIN_GLOBAL_USER is None:
    raise Exception('GARMIN_GLOBAL_USER is None')
if GARMIN_GLOBAL_PASSWORD is None:
    raise Exception('GARMIN_GLOBAL_PASSWORD is None')
if GARMIN_CN_USER is None:
    raise Exception('GARMIN_CN_USER is None')
if GARMIN_CN_PASSWORD is None:
    raise Exception('GARMIN_CN_PASSWORD is None')

GARMIN_GLOBAL_TOKEN = None
GARMIN_GLOBAL_TOKEN_FILE = "garmin_global_token.txt"
GARMIN_CN_TOKEN = None
GARMIN_CN_TOKEN_FILE = "garmin_cn_token.txt"


# login
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


garmin_global = None
garmin_cn = None

if GARMIN_GLOBAL_TOKEN_STORE is not None:
    logger.info("国际账号，验证缓存中的token。")
    garmin_global = check_token(GARMIN_GLOBAL_TOKEN_STORE)
if garmin_global is None:
    send_push_plus('国际账号缓存token过期，请更新。')
if garmin_global is None:
    try:
        logger.info("国际账号，验证本地文件中的token。")
        garmin_global = check_token(read_file_contents(GARMIN_GLOBAL_TOKEN_FILE))
    except Exception as e:
        logger.info(f"Error checking global token: {e}")
        garmin_global = None
if garmin_global is None:
    logger.info("国际账号，没有缓存的token，先进行登录。")
    garmin_global = login(GARMIN_GLOBAL_USER, GARMIN_GLOBAL_PASSWORD, False)
    logger.info("国际账号，登录成功。")
    GARMIN_GLOBAL_TOKEN = garmin_global.garth.dumps()
    write_to_file(GARMIN_GLOBAL_TOKEN_FILE, GARMIN_GLOBAL_TOKEN)
    logger.info("国际账号，保存token到本地。")

if GARMIN_CN_TOKEN_STORE is not None:
    logger.info("国内账号，验证缓存中的token。")
    garmin_cn = check_token(GARMIN_CN_TOKEN_STORE)
if garmin_cn is None:
    send_push_plus('国内账号缓存token过期，请更新。')
if garmin_cn is None:
    try:
        logger.info("国内账号，验证本地文件中的token。")
        garmin_cn = check_token(read_file_contents(GARMIN_CN_TOKEN_FILE))
    except Exception as e:
        logger.info(f"Error checking global token: {e}")
        garmin_cn = None

if garmin_cn is None:
    logger.info("国内账号，没有缓存的token，先进行登录。")
    garmin_cn = login(GARMIN_CN_USER, GARMIN_CN_PASSWORD, True)
    logger.info("国内账号，登录成功。")
    GARMIN_CN_TOKEN = garmin_cn.garth.dumps()
    write_to_file(GARMIN_CN_TOKEN_FILE, GARMIN_CN_TOKEN)
    logger.info("国内账号，保存token到本地。")

activities_cn_cache = []
query_for_date = []


def exists_activity(global_activity_start_time):
    logger.info(f"根据活动时间判断是否需要上传。{global_activity_start_time}")
    for_date = global_activity_start_time[:10]
    is_query_for_date = for_date in query_for_date
    if not is_query_for_date:
        logger.info("日期不在查询日期内，新查询。")
        end_date = datetime.datetime.strptime(for_date, '%Y-%m-%d')
        date_list = [(end_date - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        for date in date_list:
            query_for_date.append(date)

        for activity_cn in garmin_cn.get_activities_by_date(startdate=date_list[-1], enddate=for_date):
            activities_cn_cache.append(activity_cn)

    for activity in activities_cn_cache:
        if activity["startTimeLocal"] == global_activity_start_time:
            logger.info("活动已存在，无需上传。")
            return True

    return False


def sync_activity(global_activity_id):
    if not os.path.exists(GARMIN_ACTIVITY_DOWNLOAD_PATH):
        os.mkdir(GARMIN_ACTIVITY_DOWNLOAD_PATH)
    data = garmin_global.download_activity(global_activity_id, dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL)
    logger.info(f"从国际下载活动 id:{global_activity_id}")
    output_file = f"{GARMIN_ACTIVITY_DOWNLOAD_PATH}/{global_activity_id}.zip"
    if os.path.exists(output_file):
        os.remove(output_file)
    with open(output_file, 'wb') as fb:
        fb.write(data)

    extract_path = f"{GARMIN_ACTIVITY_DOWNLOAD_PATH}/{global_activity_id}_tmp"
    if not os.path.exists(extract_path):
        os.mkdir(extract_path)
    with zipfile.ZipFile(output_file, 'r') as zip:
        zip.extractall(extract_path)
    os.remove(output_file)
    for f in os.listdir(extract_path):
        path = os.path.join(extract_path, f)
        garmin_cn.upload_activity(path)
        logger.info(f"上传到cn服务器. file:{path}")
        os.remove(path)
    os.rmdir(extract_path)


activities_cn = garmin_cn.get_activities(0, 1)
activities_global = garmin_global.get_activities(0, 1)
logger.info(activities_cn[0])
logger.info(activities_global[0])
last_activity_start_time_cn = activities_cn[0]["startTimeLocal"]
last_activity_start_time_global = activities_global[0]["startTimeLocal"]

if last_activity_start_time_cn == last_activity_start_time_global:
    logger.info("最新两个账号最新的活动时间相同，无需同步。")
else:
    start = 0
    limit = GARMIN_SYNC_NUM
    sync_activity_count = 0
    while True:
        activities_global = garmin_global.get_activities(start, limit)
        logger.info(f"下载国际账号的活动。start:{start}, limit:{limit}")
        if len(activities_global) == 0:
            logger.info("没有更多活动。结束。")
            break

        for activity_global in activities_global:
            activity_id = activity_global.get("activityId")
            start_time_local = activity_global.get("startTimeLocal")
            if exists_activity(start_time_local):
                logger.info("活动已存在，无需上传。结束同步。")
                sys.exit(0)
            else:
                sync_activity(activity_id)
                sync_activity_count += 1

        if len(activities_global) < limit:
            logger.info("没有更多活动。结束。")
            break
        start += limit
    send_push_plus(f"共同步 {sync_activity_count} 个活动。")