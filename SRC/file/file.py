import time
from datetime import datetime

import numpy as np

from SRC.file.utilities import hours_to_seconds
from SRC.ftp.ftp import ftp_get_creation_date, ftp_download_file, ftp_delete_file
from SRC.settings.settings import settings
from SRC.variables import filePathMeasurements, filePathCSV

settings = settings


def convert_csv_to_numpy():
    try:
        dtypes = [('fecha', 'U8'), ('peso', 'f2')]
        # Load the data from the CSV file
        data = np.genfromtxt(filePathCSV, delimiter=',', names=True, dtype=dtypes)

        # Separate the columns into individual arrays
        dates = data['fecha']
        weights = data['peso']

        seconds: np.ndarray = hours_to_seconds(dates)

        creation: datetime = ftp_get_creation_date(**settings)
        creation_midnight = datetime(creation.year, creation.month, creation.day)
        creation_unix: int = int(time.mktime(creation_midnight.timetuple()))
        del creation
        del creation_midnight

        seconds += creation_unix

        return seconds, weights

    except FileNotFoundError:
        print(f"Error: The file indicadores.csv does not exist.")
        return None, None


def save_bin(date: np.ndarray, weights: np.ndarray) -> None:
    np.savez_compressed(filePathMeasurements, date=date, weights=weights)
    return None


def load_bin() -> tuple[np.ndarray, np.ndarray]:
    try:
        loaded = np.load(filePathMeasurements)
        return loaded['date'], loaded['weights']
    except FileNotFoundError:
        return np.array([]), np.array([])


def append_indicadores_history():
    ftp_download_file(**settings)
    csv_date, csv_weights = convert_csv_to_numpy()
    history_date, history_weights = load_bin()
    history_date = np.append(history_date, csv_date)
    history_weights = np.append(history_weights, csv_weights)
    mask_sort = np.argsort(history_date)
    history_date = history_date[mask_sort]
    history_weights = history_weights[mask_sort]
    ftp_delete_file(**settings)
    save_bin(history_date, history_weights)
