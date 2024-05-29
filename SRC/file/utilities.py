import numpy as np


def hours_to_seconds(dates: np.ndarray) -> np.ndarray:
    vectorized_hour = np.vectorize(lambda x: x[:2])
    vectorized_minutes = np.vectorize(lambda x: x[3:5])
    hours = vectorized_hour(dates).astype(np.uint8)
    minutes = vectorized_minutes(dates).astype(np.uint8)
    pm = np.char.endswith(dates, 'PM')
    twelve = hours == 12
    hours[twelve] = 0
    hours[pm] += 12
    seconds_of_day = hours * 3600 + minutes * 60
    return seconds_of_day
