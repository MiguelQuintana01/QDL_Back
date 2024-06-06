import time
from datetime import datetime

from src.utilities import now_unix


def is_created_more_24h(date: datetime):
    file_date = int(time.mktime(date.timetuple()))
    now: int = now_unix()
    return 86400 < now - file_date
