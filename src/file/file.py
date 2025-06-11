import io
import os.path
import time
from datetime import datetime

import numpy as np
import pandas as pd
from starlette.responses import StreamingResponse, FileResponse

from src.file.api import convert_list_unix_to_iso8601
from src.file.utilities import hours_to_seconds_gmt, get_creation_date
from src.ftp.ftp import ftp_get_creation_date, ftp_download_file, ftp_delete_file
from src.settings.settings import get_settings
from src.utilities import unix_midnight_local_today, get_gmt, datetime_to_unix, convert_yymmddhhmm_to_date, now_unix
from src.variables import Globs


def convert_csv_to_numpy():
    try:

        dtypes = [('fecha', 'uint32'), ('peso', 'float')]

        # Load the data from the CSV file
        path_csv = os.path.abspath(Globs.filePathCSV)
        data = np.genfromtxt(path_csv, delimiter=',', names=True, dtype=dtypes)
        # Separate the columns into individual arrays
        dates_yymmddhhmm = data['fecha']
        dates = np.array([datetime_to_unix(convert_yymmddhhmm_to_date(date)) for date in dates_yymmddhhmm])

        weights = data['peso']
        print(dates)
        save_bin_weight(Globs.pathCSVtoNpz, dates, weights)
        return load_bin(Globs.pathCSVtoNpz)

        # seconds_of_server: np.ndarray = hours_to_seconds_gmt(dates)
        #
        # creation: datetime = ftp_get_creation_date(**get_settings())
        # if creation.year >= 2200:
        #     creation = get_creation_date(Globs.filePathCSV)
        # creation_midnight = datetime(creation.year, creation.month, creation.day)
        # creation_unix: int = int(time.mktime(creation_midnight.timetuple()))
        #
        # del creation
        # del creation_midnight
        #
        # seconds_gmt = (creation_unix + seconds_of_server).astype(np.uint64)
        #
        # save_bin_weight(Globs.pathCSVtoNpz, seconds_gmt, weights)
        # return load_bin(Globs.pathCSVtoNpz)

    except Exception as e:
        print(f"Error: convert_to_numpy {e}")
        return np.array([]), np.array([])


def save_bin_weight(file_path: str, date: np.ndarray, weights: np.ndarray) -> bool:
    try:
        np.savez_compressed(file_path, date=date, weights=weights)
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
    history_date, history_weights = load_bin(Globs.filePathMeasurements)

    try:
        csv_date, csv_weights = convert_csv_to_numpy()

        csv_date_mask = csv_date > np.max(history_date) if history_date > 0 else np.full_like(csv_date, True, np.bool_)
        csv_date = csv_date[csv_date_mask]
        csv_weights = csv_weights[csv_date_mask]

        history_date = np.append(history_date, csv_date)
        history_weights = np.append(history_weights, csv_weights)
    except Exception as e:
        print(f"An error occurred while converting CSV to NumPy: {e}")
    finally:
        history_date, history_weights = order_measures_for_date(history_date, history_weights)
        return history_date, history_weights


def append_indicadores_history() -> tuple[np.ndarray, np.ndarray]:
    ftp_download_file(**get_settings())
    history_date, history_weights = get_all_measures()
    save_bin_weight(Globs.filePathMeasurements, history_date, history_weights)
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


def convert_metas_to_csv():
    from src.weights.api import get_weights_for_metas
    dict_data = get_weights_for_metas()

    table_lists = dict_data['table']
    only_dates_times = convert_list_unix_to_iso8601(np.array(table_lists)[:, 0].tolist(), get_gmt())
    for idx in range(len(table_lists)):
        table_lists[idx][0] = only_dates_times[idx][0:10]

    start_day_add = dict_data['star_day_add']
    headers = (['Date'] + (['Start day'] if start_day_add else []) +
               ['Toma ' + str(idx + 1) for idx in range(len(table_lists[0]) + (- 3 if start_day_add else - 2))] +
               ['Total'])

    df = pd.DataFrame(table_lists, columns=headers)

    buffer = io.StringIO()

    df.to_csv(buffer, index=False)

    buffer.seek(0)

    response = StreamingResponse(buffer, media_type="text/csv")

    response.headers["Content-Disposition"] = "attachment; filename=datos.csv"

    return response


def verify_csv_file():
    try:
        ftp_download_file(**get_settings())
        dates, _ = get_all_measures()
        if now_unix() - np.max(dates) >= Globs.update_if_not_use_in:
            append_indicadores_history()
            return "The file 'indicadores.csv' has appended to the history."
        else:
            return "The file 'indicadores.csv' has not been deleted and remains in the scale."
    except Exception as e:
        return f"Error with ftp: {e}"


def get_weight(start: int, end: int):
    history_dates, history_weights = get_all_measures()
    if history_dates.size <= 0:
        return history_dates, history_weights
    mask_of_period = np.logical_and(history_dates >= start, history_dates <= end)
    history_dates = history_dates[mask_of_period]
    history_weights = history_weights[mask_of_period]
    return history_dates, history_weights


def get_weights(start: int, end: int) -> dict:
    history_dates, history_weights = get_weight(start, end)
    dict_measures = {"fecha": history_dates.tolist(),
                     "peso": history_weights.tolist()}
    return dict_measures


async def download_file():
    if not os.path.exists(Globs.filePathMeasurements):
        return {"Error": "File not found"}
    return FileResponse(Globs.filePathMeasurements, media_type='application/octet-stream', filename=Globs.filePathMeasurements)


def download_csv(df: pd.DataFrame):
    buffer = io.StringIO()

    df.to_csv(buffer, index=False)

    buffer.seek(0)

    response = StreamingResponse(buffer, media_type="text/csv")

    response.headers["Content-Disposition"] = "attachment; filename=datos.csv"

    return response
