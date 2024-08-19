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

GARMIN_DST_USER = 'xsi64@126.com' #os.environ.get('GARMIN_DST_USER')
GARMIN_DST_PASSWORD = 'SHAduoh@163.com' # os.environ.get('GARMIN_DST_PASSWORD')
if os.environ.get('GARMIN_DST_IS_CN') is not None:
    GARMIN_DST_IS_CN = bool(os.environ.get('GARMIN_DST_IS_CN'))
else:
    GARMIN_DST_IS_CN = False
GARMIN_DST_IS_CN = True
GARMIN_DST_TOKEN_STORE = 'W3sib2F1dGhfdG9rZW4iOiAiZTFjMmZhZGQtMThkYS00NmMzLWI3ZmMtZDgwZGQ5OTU0MDA0IiwgIm9hdXRoX3Rva2VuX3NlY3JldCI6ICJ5aFlVU0FOT2QydXRjSXVFbTdxUkNKelhFZ3JLb05pcTdIOCIsICJtZmFfdG9rZW4iOiBudWxsLCAibWZhX2V4cGlyYXRpb25fdGltZXN0YW1wIjogbnVsbCwgImRvbWFpbiI6ICJnYXJtaW4uY24ifSwgeyJzY29wZSI6ICJDT01NVU5JVFlfQ09VUlNFX1JFQUQgR0FSTUlOUEFZX1dSSVRFIEdPTEZfQVBJX1JFQUQgQVRQX1JFQUQgR0hTX1NBTUQgR0hTX1VQTE9BRCBJTlNJR0hUU19SRUFEIENPTU1VTklUWV9DT1VSU0VfV1JJVEUgQ09OTkVDVF9XUklURSBHQ09GRkVSX1dSSVRFIEdBUk1JTlBBWV9SRUFEIERUX0NMSUVOVF9BTkFMWVRJQ1NfV1JJVEUgR09MRl9BUElfV1JJVEUgSU5TSUdIVFNfV1JJVEUgUFJPRFVDVF9TRUFSQ0hfUkVBRCBPTVRfQ0FNUEFJR05fUkVBRCBPTVRfU1VCU0NSSVBUSU9OX1JFQUQgR0NPRkZFUl9SRUFEIENPTk5FQ1RfUkVBRCBBVFBfV1JJVEUiLCAianRpIjogImYwY2M1MGNlLWU4MmYtNGQ3ZC1hZTdhLTAyYjVjYThlOTA5ZCIsICJ0b2tlbl90eXBlIjogIkJlYXJlciIsICJhY2Nlc3NfdG9rZW4iOiAiZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0lzSW10cFpDSTZJbVJwTFc5aGRYUm9MWE5wWjI1bGNpMXdjbTlrTFdOdU1TMHlNREkwTFhFeEluMC5leUp6WTI5d1pTSTZXeUpCVkZCZlVrVkJSQ0lzSWtGVVVGOVhVa2xVUlNJc0lrTlBUVTFWVGtsVVdWOURUMVZTVTBWZlVrVkJSQ0lzSWtOUFRVMVZUa2xVV1Y5RFQxVlNVMFZmVjFKSlZFVWlMQ0pEVDA1T1JVTlVYMUpGUVVRaUxDSkRUMDVPUlVOVVgxZFNTVlJGSWl3aVJGUmZRMHhKUlU1VVgwRk9RVXhaVkVsRFUxOVhVa2xVUlNJc0lrZEJVazFKVGxCQldWOVNSVUZFSWl3aVIwRlNUVWxPVUVGWlgxZFNTVlJGSWl3aVIwTlBSa1pGVWw5U1JVRkVJaXdpUjBOUFJrWkZVbDlYVWtsVVJTSXNJa2RJVTE5VFFVMUVJaXdpUjBoVFgxVlFURTlCUkNJc0lrZFBURVpmUVZCSlgxSkZRVVFpTENKSFQweEdYMEZRU1Y5WFVrbFVSU0lzSWtsT1UwbEhTRlJUWDFKRlFVUWlMQ0pKVGxOSlIwaFVVMTlYVWtsVVJTSXNJazlOVkY5RFFVMVFRVWxIVGw5U1JVRkVJaXdpVDAxVVgxTlZRbE5EVWtsUVZFbFBUbDlTUlVGRUlpd2lVRkpQUkZWRFZGOVRSVUZTUTBoZlVrVkJSQ0pkTENKcGMzTWlPaUpvZEhSd2N6b3ZMMlJwWVhWMGFDNW5ZWEp0YVc0dVkyNGlMQ0p5WlhadlkyRjBhVzl1WDJWc2FXZHBZbWxzYVhSNUlqcGJJa2RNVDBKQlRGOVRTVWRPVDFWVUlsMHNJbU5zYVdWdWRGOTBlWEJsSWpvaVZVNUVSVVpKVGtWRUlpd2laWGh3SWpveE56STBNVE0wTVRjMExDSnBZWFFpT2pFM01qUXdNek00TkRnc0ltZGhjbTFwYmw5bmRXbGtJam9pTlRsa01ETm1NMk10WkRVek5pMDBORGcwTFdFd09Ua3RaVEU1T1dNM1pqUTVaakk0SWl3aWFuUnBJam9pWmpCall6VXdZMlV0WlRneVppMDBaRGRrTFdGbE4yRXRNREppTldOaE9HVTVNRGxrSWl3aVkyeHBaVzUwWDJsa0lqb2lSMEZTVFVsT1gwTlBUazVGUTFSZlRVOUNTVXhGWDBGT1JGSlBTVVJmUkVraWZRLnBzbTM5bnZfUFpCeXZxaUdyelBYOUdkdEs4WXUzMkh2STJvazJ0SzBlQmNmd19qV2pjeWREMkcwc2lURDdJbEhodmZ3dTFKX0J6TVlLMzJCcE5wdnpMclN4bFdkSkpxMXowcWNJM0Y3U2tMZXFQWjZENkt4eUtUM1NsS2t4UmZ2elh2Z095cEZrTnF3bWN1MUZTcjVVZDRSeko3MlNsai1tcWtTeDZmaVRSNnVVWVhUZDZab1lTZzA1N2diWmJ4a0x4UkZNMHRwVDZJTFEySF9kRjhXRXZHYVpPaVFnS0JDOVlVd2oya0Q2WHNLMTlJcC10NEJ6TWJvVGhVX0djMkdXbFQwZFZBdE9naHRVWVRjeDJPSU0zTEliaE1IRkRRMkhzRndJYklGSzQ1bl9qUHFSVVhJSVhfWjI0X1hjeFVoekdmd2J2NHVwcDVfT0VaYzk4QmF6dyIsICJyZWZyZXNoX3Rva2VuIjogImV5SnlaV1p5WlhOb1ZHOXJaVzVXWVd4MVpTSTZJbVpoTnpCbE9EbGxMVEZrT1RJdE5EbG1OUzFpTnpBNUxURmtabUZtTmpGbE9XSTNOQ0lzSW1kaGNtMXBia2QxYVdRaU9pSTFPV1F3TTJZell5MWtOVE0yTFRRME9EUXRZVEE1T1MxbE1UazVZemRtTkRsbU1qZ2lmUT09IiwgImV4cGlyZXNfaW4iOiAxMDAzMjUsICJleHBpcmVzX2F0IjogMTcyNDEzNDE4MywgInJlZnJlc2hfdG9rZW5fZXhwaXJlc19pbiI6IDI1OTE5OTksICJyZWZyZXNoX3Rva2VuX2V4cGlyZXNfYXQiOiAxNzI2NjI1ODU3fV0=' # os.environ.get('GARMIN_DST_TOKEN_STORE')
GARMIN_SRC_USER = 'xsi640@hotmail.com' # os.environ.get('GARMIN_SRC_USER')
GARMIN_SRC_PASSWORD = 'SHAduoh@163.com' # os.environ.get('GARMIN_SRC_PASSWORD')
if os.environ.get('GARMIN_SRC_IS_CN') is not None:
    GARMIN_SRC_IS_CN = bool(os.environ.get('GARMIN_SRC_IS_CN'))
else:
    GARMIN_SRC_IS_CN = False
GARMIN_SRC_IS_CN = False
GARMIN_SRC_TOKEN_STORE = 'W3sib2F1dGhfdG9rZW4iOiAiNTkyODhjODEtNGQzZC00NTM3LTljNDMtOTk0YTM4ODA1OTU4IiwgIm9hdXRoX3Rva2VuX3NlY3JldCI6ICJad1dpbDRuVkcwUG80SHZLWTNYRzRxZUlDdGxycnV2OGQxTSIsICJtZmFfdG9rZW4iOiBudWxsLCAibWZhX2V4cGlyYXRpb25fdGltZXN0YW1wIjogbnVsbCwgImRvbWFpbiI6ICJnYXJtaW4uY29tIn0sIHsic2NvcGUiOiAiQ09NTVVOSVRZX0NPVVJTRV9SRUFEIEdBUk1JTlBBWV9XUklURSBHT0xGX0FQSV9SRUFEIEFUUF9SRUFEIEdIU19TQU1EIEdIU19VUExPQUQgSU5TSUdIVFNfUkVBRCBDT01NVU5JVFlfQ09VUlNFX1dSSVRFIENPTk5FQ1RfV1JJVEUgR0NPRkZFUl9XUklURSBHQVJNSU5QQVlfUkVBRCBEVF9DTElFTlRfQU5BTFlUSUNTX1dSSVRFIEdPTEZfQVBJX1dSSVRFIElOU0lHSFRTX1dSSVRFIFBST0RVQ1RfU0VBUkNIX1JFQUQgT01UX0NBTVBBSUdOX1JFQUQgT01UX1NVQlNDUklQVElPTl9SRUFEIEdDT0ZGRVJfUkVBRCBDT05ORUNUX1JFQUQgQVRQX1dSSVRFIiwgImp0aSI6ICI0MzljNjk0ZS1lYjg1LTQ0YTQtODk1Mi05OWQ0NGVkZDEzMDUiLCAidG9rZW5fdHlwZSI6ICJCZWFyZXIiLCAiYWNjZXNzX3Rva2VuIjogImV5SmhiR2NpT2lKU1V6STFOaUlzSW5SNWNDSTZJa3BYVkNJc0ltdHBaQ0k2SW1ScExXOWhkWFJvTFhOcFoyNWxjaTF3Y205a0xUSXdNalF0Y1RFaWZRLmV5SnpZMjl3WlNJNld5SkJWRkJmVWtWQlJDSXNJa0ZVVUY5WFVrbFVSU0lzSWtOUFRVMVZUa2xVV1Y5RFQxVlNVMFZmVWtWQlJDSXNJa05QVFUxVlRrbFVXVjlEVDFWU1UwVmZWMUpKVkVVaUxDSkRUMDVPUlVOVVgxSkZRVVFpTENKRFQwNU9SVU5VWDFkU1NWUkZJaXdpUkZSZlEweEpSVTVVWDBGT1FVeFpWRWxEVTE5WFVrbFVSU0lzSWtkQlVrMUpUbEJCV1Y5U1JVRkVJaXdpUjBGU1RVbE9VRUZaWDFkU1NWUkZJaXdpUjBOUFJrWkZVbDlTUlVGRUlpd2lSME5QUmtaRlVsOVhVa2xVUlNJc0lrZElVMTlUUVUxRUlpd2lSMGhUWDFWUVRFOUJSQ0lzSWtkUFRFWmZRVkJKWDFKRlFVUWlMQ0pIVDB4R1gwRlFTVjlYVWtsVVJTSXNJa2xPVTBsSFNGUlRYMUpGUVVRaUxDSkpUbE5KUjBoVVUxOVhVa2xVUlNJc0lrOU5WRjlEUVUxUVFVbEhUbDlTUlVGRUlpd2lUMDFVWDFOVlFsTkRVa2xRVkVsUFRsOVNSVUZFSWl3aVVGSlBSRlZEVkY5VFJVRlNRMGhmVWtWQlJDSmRMQ0pwYzNNaU9pSm9kSFJ3Y3pvdkwyUnBZWFYwYUM1bllYSnRhVzR1WTI5dElpd2ljbVYyYjJOaGRHbHZibDlsYkdsbmFXSnBiR2wwZVNJNld5SkhURTlDUVV4ZlUwbEhUazlWVkNKZExDSmpiR2xsYm5SZmRIbHdaU0k2SWxWT1JFVkdTVTVGUkNJc0ltVjRjQ0k2TVRjeU5ERXpOamMyTkN3aWFXRjBJam94TnpJME1ETXpPRFUxTENKbllYSnRhVzVmWjNWcFpDSTZJamxqWXpRek5tUXhMV1ZrTkdFdE5EbG1NUzA0WldVeExXVXlZMk0zTkRsa01tRXdPQ0lzSW1wMGFTSTZJalF6T1dNMk9UUmxMV1ZpT0RVdE5EUmhOQzA0T1RVeUxUazVaRFEwWldSa01UTXdOU0lzSW1Oc2FXVnVkRjlwWkNJNklrZEJVazFKVGw5RFQwNU9SVU5VWDAxUFFrbE1SVjlCVGtSU1QwbEVYMFJKSW4wLktoVkpjNDZ4YXhqLUNlc0c4TzN2dDRSRU9BMC12b2RVMDVPSWtWOWN2T1puVUVWTnJpUF9pczhwTWRqaTY1ek1yejNkaHlESmNUamlFb2hPeWNYbjh6NEk1YnNrSThBN1RVaHlNeUdjdnhhUkpESkFXZHMxSHRvaVNlaGpVQzVibkdjazduU0N2eDdpWmRJNmJnOFVXQnAtV0laV0lvckUyWF9RWkVpczhuYnBBTlJ5djFEYmxfaFlBeFpTeXJPN2s5WW5NSDFxY2NaTTFSUDN1YURYclhoTk9UX2kwOXZJVzRRVlVoLTgwMzhjbDFPOVRoTDdLcG5lYnJ3a0R3bnVGZVZjaEFNLV9iWGtYakxMSWpxNldHVU9fTXQ3YUNIN0R5cTc0R2k2bFBZNkh2VlpYdGlZQkFsSG5IRE1hS3Z0NkgxVGJFUlVTWF92QkRzUnlSU3lmZyIsICJyZWZyZXNoX3Rva2VuIjogImV5SnlaV1p5WlhOb1ZHOXJaVzVXWVd4MVpTSTZJakl3WmpBNVpETmtMV1ptTWpndE5HSmlaQzA0WWpCakxXVmtObUpsT1dOaE16azFNeUlzSW1kaGNtMXBia2QxYVdRaU9pSTVZMk0wTXpaa01TMWxaRFJoTFRRNVpqRXRPR1ZsTVMxbE1tTmpOelE1WkRKaE1EZ2lmUT09IiwgImV4cGlyZXNfaW4iOiAxMDI5MDgsICJleHBpcmVzX2F0IjogMTcyNDEzNjc3MywgInJlZnJlc2hfdG9rZW5fZXhwaXJlc19pbiI6IDI1OTE5OTksICJyZWZyZXNoX3Rva2VuX2V4cGlyZXNfYXQiOiAxNzI2NjI1ODY0fV0=' # os.environ.get('GARMIN_SRC_TOKEN_STORE')
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

if last_activity_start_time_src == last_activity_start_time_dst:
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
