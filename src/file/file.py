import os.path
import time
from datetime import datetime, timezone

import numpy as np

from src.file.utilities import hours_to_seconds_gmt
from src.ftp.ftp import ftp_get_creation_date, ftp_download_file, ftp_delete_file
from src.settings.settings import settings
from src.utilities import get_gmt
from src.variables import filePathMeasurements, filePathCSV

settings = settings


def convert_csv_to_numpy():
    try:

        dtypes = [('fecha', 'U8'), ('peso', 'float')]
        # Load the data from the CSV file
        data = np.genfromtxt(filePathCSV, delimiter=',', names=True, dtype=dtypes)

        # Separate the columns into individual arrays
        dates = data['fecha']
        weights = data['peso']

        seconds_of_server: np.ndarray = hours_to_seconds_gmt(dates)

        creation: datetime = ftp_get_creation_date(**settings)
        creation_midnight = datetime(creation.year, creation.month, creation.day)
        creation_unix: int = int(time.mktime(creation_midnight.timetuple()))

        del creation
        del creation_midnight

        seconds_gmt = (creation_unix + seconds_of_server).astype(np.uint64)

        return seconds_gmt, weights

    except FileNotFoundError:
        print(f"Error: The file indicadores.csv does not exist.")
        return None, None


def save_bin(date: np.ndarray, weights: np.ndarray) -> None:
    np.savez_compressed(filePathMeasurements, date=date, weights=weights)
    return None


def load_bin() -> tuple[np.ndarray, np.ndarray]:
    if not os.path.isfile(filePathMeasurements):
        return np.array([]), np.array([])

    try:
        loaded = np.load(filePathMeasurements)
        return loaded['date'], loaded['weights']
    except FileNotFoundError:
        return np.array([]), np.array([])


def order_measures_for_date(history_date: np.ndarray, history_weights: np.ndarray):
    indices_sorted_for_date = np.argsort(history_date)
    indices_order_descending = indices_sorted_for_date[::-1]
    history_date = history_date[indices_order_descending]
    history_weights = history_weights[indices_order_descending]
    return history_date, history_weights


def get_all_measures():
    history_date, history_weights = load_bin()

    try:
        csv_date, csv_weights = convert_csv_to_numpy()
        history_date = np.append(history_date, csv_date)
        history_weights = np.append(history_weights, csv_weights)
    except Exception as e:
        print(f"An error occurred while converting CSV to NumPy: {e}")

    history_date, history_weights = order_measures_for_date(history_date, history_weights)
    return history_date, history_weights


def append_indicadores_history() -> tuple[np.ndarray, np.ndarray]:
    ftp_download_file(**settings)
    history_date, history_weights = get_all_measures()
    ftp_delete_file(**settings)
    save_bin(history_date, history_weights)
    return history_date, history_weights
