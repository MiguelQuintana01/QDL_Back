import datetime

import numpy as np
from fastapi import APIRouter


api = APIRouter()


def convert_list_unix_to_iso8601(dates_unix: list[float | int] | np.ndarray, gmt: int) -> list[str]:
    offset = datetime.timezone(datetime.timedelta(hours=gmt))
    dates = [
        datetime.datetime.fromtimestamp(unix).replace(tzinfo=offset).strftime('%Y-%m-%d %H:%M:%S')
        for unix in dates_unix
    ]
    return dates





