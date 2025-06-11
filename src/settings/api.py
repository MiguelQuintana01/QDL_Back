from typing import List

import numpy as np
from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel

from src.file.file import save_bin_weight, load_bin
from src.settings.settings import save_dict_as_json, load_json_as_dict
from src.variables import Globs


class TimesWeightsMetas(BaseModel):
    dates: List
    weights: List


api = APIRouter()


def convert_to_numpy(metas_weights: TimesWeightsMetas):
    dates = np.array(metas_weights.dates, dtype=np.uint64)
    weights = np.array(metas_weights.weights, dtype=np.float32)
    return dates, weights


@api.post("")
async def download_ftp_file(
        ftp_server: str = Form(...),
        ftp_port: int = Form(default=21),  # The default port of FTP is 21
        username: str = Form(default=""),
        password: str = Form(default=""),
):
    try:
        settings = {'ftp_server': ftp_server, 'ftp_port': ftp_port, 'username': username, 'password': password}
        save_dict_as_json(settings, Globs.fileSettings)
        return "Settings updated"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.post("/metas")
async def time_metas(metas: TimesWeightsMetas):
    try:
        metas.dates, metas.weights = convert_to_numpy(metas)

        unique_elements, counts = np.unique(metas.dates, return_counts=True)

        # Verifica si algún elemento tiene más de una aparición
        if np.any(counts > 1):
            raise "Error, las horas no se pueden repetir"

        dates_sorted = np.argsort(metas.dates)
        metas.dates = metas.dates[dates_sorted]
        metas.weights = metas.weights[dates_sorted]
        save_bin_weight(Globs.fileMetasWeights, metas.dates, metas.weights)
        return "Settings update"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.get("")
async def read_settings():
    try:
        settings_dict: dict = load_json_as_dict(Globs.fileSettings)
        settings_dict['password'] = ""
        return settings_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.get("/metas")
async def read_metas():
    try:
        metas = load_bin(Globs.fileMetasWeights)
        data = {'dates': metas[0].tolist(), 'weights': metas[1].tolist()}
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.get("/metas/reset")
async def erase_metas():
    """
        Erase the file at the given file path.

        Parameters:
        file_path (str): The path to the file to be deleted.
        """
    try:
        file_path = Globs.fileMetasWeights
        import os
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"File '{file_path}' has been erased.")
        else:
            print(f"No file found at '{file_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
