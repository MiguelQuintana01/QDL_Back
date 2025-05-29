from datetime import datetime

import numpy as np
import os


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


def get_creation_date(filePath):
    try:
        timestamp_creacion = os.path.getctime(filePath)
        fecha_creacion = datetime.fromtimestamp(timestamp_creacion)
        return fecha_creacion
    except FileNotFoundError:
        return datetime(2200, 1, 1)


def delete_file(file_path: str):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            return True
        else:
            print(f"File does not exist: {file_path}")
            return False
    except Exception as e:
        print(f"An error occurred while trying to delete the file: {e}")
        return False


def int_to_datetime(value: int) -> datetime:
    """Converts an integer in yymmddhhmm format to a datetime object. 📆✨

    Args:
        value (int): A date/time represented as an integer yymmddhhmm
            (e.g., 2307151830 for 2023-07-15 18:30).

    Returns:
        datetime: A datetime instance corresponding to the parsed value.

    Raises:
        ValueError: If the integer cannot be parsed into a valid date/time.
    """
    s = str(value).zfill(10)  # Pad with leading zeros if needed 🧩
    yy = int(s[0:2])
    mm = int(s[2:4])
    dd = int(s[4:6])
    hh = int(s[6:8])
    mi = int(s[8:10])

    year = 2000 + yy  # Adjust two-digit year to full year 📜
    try:
        return datetime(year, mm, dd, hh, mi)
    except ValueError as e:
        raise ValueError(f"Invalid date/time components: {e}")