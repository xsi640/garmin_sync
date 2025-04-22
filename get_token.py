from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
)


def login(username, password, is_cn):
    try:
        garmin = Garmin(email=username, password=password, is_cn=is_cn)
        garmin.login()
        print(f"token: {garmin.garth.dumps()}")
    except GarminConnectAuthenticationError as e:
        raise Exception(f"Authentication error: {e}")
    except Exception as e:
        raise Exception(f"Error logging in: {e}")


if __name__ == '__main__':
    login("xsi640@hotmail.com", "SHAduoh@163.com", False)

# GARMIN_DST_IS_CN = True
# GARMIN_DST_TOKEN_STORE =
# GARMIN_DST_USER = xsi64@126.com
# GARMIN_DST_PASSWORD =

# GARMIN_DST_IS_CN = False
# GARMIN_DST_USER = xsi640@hotmail.com
# GARMIN_DST_PASSWORD =
# GARMIN_DST_TOKEN_STORE =
