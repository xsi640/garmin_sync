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
    login("", "", False)