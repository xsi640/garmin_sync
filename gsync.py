import logging
import datetime
import os
import zipfile

import requests
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GARMIN_ACTIVITY_DOWNLOAD_PATH = "activities"
PUSH_PLUS_TOKEN = os.environ.get('PUSH_PLUS_TOKEN')


def send_push_plus(msg):
    if PUSH_PLUS_TOKEN is not None:
        url = 'http://www.pushplus.plus/send'
        data = {
            "token": PUSH_PLUS_TOKEN,
            "title": "Garmin账号同步",
            "content": msg
        }
        requests.post(url, data=data)


class GSync:
    activities_dst_cache = []
    query_for_date = []

    def __init__(self, garmin_src, garmin_dst, sync_num):
        self.garmin_src = garmin_src
        self.garmin_dst = garmin_dst
        self.sync_num = sync_num

    def exists_activity(self, src_activity_start_time):
        logger.info(f"根据活动时间判断是否需要上传。{src_activity_start_time}")
        for_date = src_activity_start_time[:10]
        is_query_for_date = for_date in self.query_for_date
        if not is_query_for_date:
            logger.info("日期不在查询日期内，新查询。")
            end_date = datetime.datetime.strptime(for_date, '%Y-%m-%d')
            date_list = [(end_date - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
            for date in date_list:
                self.query_for_date.append(date)

            for activity_dst in self.garmin_dst.get_activities_by_date(startdate=date_list[-1], enddate=for_date):
                self.activities_dst_cache.append(activity_dst)

        for activity in self.activities_dst_cache:
            if activity["startTimeLocal"] == src_activity_start_time:
                logger.info("活动已存在，无需上传。")
                return True

        return False

    def sync_activity(self, src_activity_id):
        if not os.path.exists(GARMIN_ACTIVITY_DOWNLOAD_PATH):
            os.mkdir(GARMIN_ACTIVITY_DOWNLOAD_PATH)
        data = self.garmin_src.download_activity(src_activity_id, dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL)
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
            self.garmin_dst.upload_activity(path)
            logger.info(f"上传到目标服务器. file:{path}")
            os.remove(path)
        os.rmdir(extract_path)

    def sync(self):
        self.activities_dst_cache = []
        self.query_for_date = []
        activities_src = self.garmin_src.get_activities(0, 1)
        activities_dst = self.garmin_dst.get_activities(0, 1)
        logger.info(activities_src[0])
        logger.info(activities_dst[0])
        last_activity_start_time_src = activities_src[0]["startTimeLocal"]
        last_activity_start_time_dst = activities_dst[0]["startTimeLocal"]
        if last_activity_start_time_src == last_activity_start_time_dst:
            logger.info("最新两个账号最新的活动时间相同，无需同步。")
        else:
            start = 0
            limit = self.sync_num
            sync_activity_count = 0
            while True:
                activities_src = self.garmin_src.get_activities(start, limit)
                logger.info(f"下载国际账号的活动。start:{start}, limit:{limit}")
                if len(activities_src) == 0:
                    logger.info("没有更多活动。结束。")
                    break

                flag = False
                for activity_src in activities_src:
                    activity_id = activity_src.get("activityId")
                    start_time_local = activity_src.get("startTimeLocal")
                    if self.exists_activity(start_time_local):
                        logger.info("活动已存在，无需上传。结束同步。")
                        flag = True
                        break
                    else:
                        self.sync_activity(activity_id)
                        sync_activity_count += 1

                if flag:
                    break
                if len(activities_src) < limit:
                    logger.info("没有更多活动。结束。")
                    break
                start += limit
            send_push_plus(f"共同步 {sync_activity_count} 个活动。")
