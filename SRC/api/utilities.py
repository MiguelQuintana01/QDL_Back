import time
from datetime import datetime

from SRC.utilities import midnight


def is_yesterday_date(date: datetime):
    file_date = int(time.mktime(date.timetuple()))
    midnight_date = int(time.mktime(midnight().timetuple()))
    return file_date < midnight_date
