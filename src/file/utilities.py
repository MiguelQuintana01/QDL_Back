import numpy as np

from src.settings.settings import settings


def hours_to_seconds_gmt(dates: np.ndarray) -> np.ndarray:
    vectorized_hour = np.vectorize(lambda x: x[:2])
    vectorized_minutes = np.vectorize(lambda x: x[3:5])
    hours = vectorized_hour(dates).astype(np.int32)
    minutes = vectorized_minutes(dates).astype(np.int32)
    pm = np.char.endswith(dates, 'PM')
    twelve = hours == 12
    hours[twelve] = 0
    hours[pm] += 12
    seconds_of_day = (hours * 3600 + minutes * 60).astype(np.int32)
    return seconds_of_day
