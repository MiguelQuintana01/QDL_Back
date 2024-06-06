import io
import os

import numpy as np
import pandas as pd
from starlette.responses import StreamingResponse

from src.file.api import convert_list_unix_to_iso8601
from src.file.file import load_bin, order_measures_for_date
from src.utilities import now_unix
from src.variables import fileMeta


def save_bin_meta(meta: float) -> bool:
    try:
        date_bin, meta_bin = load_bin(fileMeta)

        meta = np.append(meta, meta_bin)
        date = np.append(now_unix(), date_bin)

        date, meta = order_measures_for_date(date, meta)
        np.savez_compressed(fileMeta, date=date, meta=meta)
        return True
    except Exception as e:
        print(e)
        return False


def delete_last_meta() -> dict:
    try:
        date_bin, meta_bin = load_bin(fileMeta)
        if date_bin.size > 1:
            date_bin, meta_bin = order_measures_for_date(date_bin, meta_bin)
            date_bin = date_bin[1:]
            meta_bin = meta_bin[1:]
            np.savez_compressed(fileMeta, date=date_bin, meta=meta_bin)
            return {"message": "Meta eliminada"}
        elif date_bin.size == 1:
            date_bin = np.array([], dtype=date_bin.dtype)
            meta_bin = np.array([], dtype=meta_bin.dtype)
            np.savez_compressed(fileMeta, date=date_bin, meta=meta_bin)
            return {"message": "Meta eliminada"}
        else:
            return {'message': "No hay metas"}
    except Exception as e:
        print(e)
        return {'message': "Error al borrar meta"}


def download_csv_metas(start: int = 0, end: int = 4102444800, gmt: int = 0):
    dict_data = load_bin(fileMeta)

    dict_data = {'dates': dict_data[0] + gmt * 3600, 'metas': dict_data[1]}

    dict_data['dates'] = convert_list_unix_to_iso8601(dict_data['dates'], gmt)

    df = pd.DataFrame(dict_data)

    buffer = io.StringIO()

    df.to_csv(buffer, index=False)

    buffer.seek(0)

    response = StreamingResponse(buffer, media_type="text/csv")

    response.headers["Content-Disposition"] = "attachment; filename=datos.csv"

    return response
