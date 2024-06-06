import io
import os.path
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from starlette.responses import StreamingResponse

from src.api.utilities import is_created_more_24h
from src.file.api import convert_list_unix_to_iso8601
from src.file.utilities import hours_to_seconds_gmt
from src.ftp.ftp import ftp_get_creation_date, ftp_download_file, ftp_delete_file
from src.settings.settings import settings
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


def save_bin_weight(date: np.ndarray, weights: np.ndarray) -> bool:
    try:
        np.savez_compressed(filePathMeasurements, date=date, weights=weights)
        return True
    except Exception as e:
        print(e)
        return False


def load_bin(file: str) -> [np.ndarray, np.ndarray]:
    """

    :param file:
    :return: dates, values
    """
    data: [np.ndarray, np.ndarray] = np.array([]), np.array([])
    if not os.path.isfile(file):
        return data

    try:
        loaded = np.load(file)
        data: [np.ndarray, np.ndarray] = [loaded[key] for key in loaded.files]
    except Exception as e:
        print(e)
    finally:
        return data


def order_measures_for_date(history_date: np.ndarray, history_weights: np.ndarray):
    """

    :param history_date:
    :param history_weights:
    :return: history_date_sorted
    :return: history_weights_sorted
    """
    indices_sorted_for_date = np.argsort(history_date)
    indices_order_descending = indices_sorted_for_date[::-1]
    history_date = history_date[indices_order_descending]
    history_weights = history_weights[indices_order_descending]
    return history_date, history_weights


def get_all_measures():
    history_date, history_weights = load_bin(filePathMeasurements)

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
    save_bin_weight(history_date, history_weights)
    return history_date, history_weights


def download_csv_weights(start: int = 0, end: int = 4102444800, gmt: int = 0):
    dict_data = get_weights(start, end)

    dict_data['fecha'] = convert_list_unix_to_iso8601(dict_data['fecha'], gmt)

    df = pd.DataFrame(dict_data)

    buffer = io.StringIO()

    df.to_csv(buffer, index=False)

    buffer.seek(0)

    response = StreamingResponse(buffer, media_type="text/csv")

    response.headers["Content-Disposition"] = "attachment; filename=datos.csv"

    return response


def verify_ftp_file():
    if is_created_more_24h(ftp_get_creation_date(**settings)):
        append_indicadores_history()
        return "The file 'indicadores.csv' has been deleted and appended to the history."
    else:
        return "The file 'indicadores.csv' has not been deleted and remains in the scale."


def get_weight(start: int, end: int):
    history_dates, history_weights = get_all_measures()
    mask_of_period = np.logical_and(history_dates >= start, history_dates <= end)
    history_dates = history_dates[mask_of_period]
    history_weights = history_weights[mask_of_period]
    return history_dates, history_weights



def get_weights(start: int, end: int) -> dict:
    history_dates, history_weights = get_weight(start, end)
    dict_measures = {"fecha": history_dates.tolist(),
                     "peso": history_weights.tolist()}
    return dict_measures
