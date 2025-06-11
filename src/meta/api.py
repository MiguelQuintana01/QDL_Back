import numpy as np
from fastapi import APIRouter, Form

from src.file.file import load_bin
from src.file.file_meta import save_bin_meta, download_csv_metas, delete_last_meta
from src.variables import Globs

api = APIRouter()


@api.post("")
def post_meta(meta: float = Form()):
    return save_bin_meta(meta)


@api.get("")
def get_meta() -> dict:
    dates, metas = load_bin(Globs.fileMeta)

    if dates.size <= 0:
        dates = np.append(dates, 943920000)
        metas = np.append(metas, 10000)
        return {'date': dates, 'meta': metas}

    date, meta = dates[0], metas[0]
    return {'date': date, 'meta': meta}


@api.get("/all")
def get_all_metas() -> dict:
    try:
        dates, metas = load_bin(Globs.fileMeta)
        return {'dates': dates.tolist(), 'metas': metas.tolist()}
    except Exception as e:
        return {'dates': np.ndarray, 'metas': np.ndarray}


@api.get("/download-csv")
def download_csv(gmt: int = Form(default=0)):
    return download_csv_metas(gmt=gmt)


@api.delete("")
def delete_last_meta_api() -> dict:
    return delete_last_meta()
