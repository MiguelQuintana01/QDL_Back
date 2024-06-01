import time
from datetime import datetime

from src.utilities import midnight_local, get_gmt


def is_yesterday_date(date: datetime):
    file_date = int(time.mktime(date.timetuple()))
    midnight_date = int(time.mktime(midnight_local().timetuple())) + get_gmt() * 3600
    return file_date < midnight_date
