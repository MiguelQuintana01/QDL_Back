import time
from datetime import datetime, timezone, timedelta



def midnight_local() -> datetime:
    # Get the current date and time
    now = datetime.now()
    # Create a datetime object for midnight of the current date
    today_midnight = datetime(now.year, now.month, now.day) - timedelta(hours=get_gmt())
    return today_midnight


def unix_midnight_local_today(**kwargs):
    try:
        return int(midnight_local().timestamp()) + get_gmt() * 3600
    except Exception as e:
        return f"Error: {e}"


def datetime_to_unix(date_time: datetime) -> int:
    try:
        return int(date_time.timestamp())
    except Exception as e:
        return f"Error with datetime to unix: {e}"


def now_unix() -> int:
    now = int(time.mktime(datetime.now().timetuple()))
    return now


def get_gmt() -> int:
    # Get the current local time
    local_time = datetime.now()

    # Get the current UTC time
    utc_time = datetime.now(timezone.utc)

    # Calculate the difference between local time and UTC time
    time_difference = local_time - utc_time.replace(tzinfo=None)

    # Convert the time difference to hours
    time_difference_hours = time_difference.total_seconds() / 3600
    return int(-6)
    # return int(time_difference_hours)
