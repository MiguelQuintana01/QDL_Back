import os

import numpy as np
from fastapi import APIRouter, Form, UploadFile, File
from starlette.responses import FileResponse

from src.file.file import download_csv_weights, verify_csv_file, get_all_measures, load_bin, convert_metas_to_csv
from src.utilities import get_gmt
from src.variables import Globs

api = APIRouter()


start_unix = 0
end_unix = 4102444800


@api.post("")
def get_weight_api(start: int = Form(default=start_unix), end: int = Form(default=end_unix)):
    verify_csv_file()

    history_dates, history_weights = get_all_measures()

    if history_dates.size > 0:
        mask = np.logical_and(start <= history_dates, history_dates <= end)
        history_dates = history_dates[mask]
        history_weights = history_weights[mask]

    dict_measures = {"fecha": history_dates.tolist(),
                     "peso": history_weights.tolist()}
    return dict_measures


@api.post("/download-csv")
def download_csv(start: int = Form(0), end: int = Form(4102444800), gmt: int = Form(0)):
    return download_csv_weights(start, end, gmt)


@api.get("/metas/download-csv")
def download_csv_metas():
    return convert_metas_to_csv()


@api.get("/metas")
def get_weights_for_metas():
    # times_metas = load_json_as_dict(fileTimesMetas)
    SECONDS_OF_DAY: int = 24 * 3600
    GMT = get_gmt() * 3600
    data_metas = load_bin(Globs.fileMetasWeights)

    data_sorted = np.argsort(data_metas[0])
    data_metas[0] = data_metas[0][data_sorted]
    data_metas[1] = data_metas[1][data_sorted]

    all_weights = get_weight_api(start=start_unix, end=end_unix)
    fecha = np.array(all_weights['fecha'])
    peso = np.array(all_weights['peso'])

    days_midnight = np.array(((fecha + GMT) // SECONDS_OF_DAY) * SECONDS_OF_DAY - GMT, np.uint64)
    hours = (fecha - days_midnight)

    not_start_day = (data_metas[0] != 0).all()
    if not_start_day:
        zero = np.array([0], dtype=np.uint64)
        data_metas[0] = np.append(zero, data_metas[0])
        data_metas[1] = np.append(zero, data_metas[1])

    hours_masks = np.array([])
    for idx, hour_meta in np.ndenumerate(data_metas[0]):
        idx = idx[0]
        if idx < data_metas[0].size - 1:
            if hours_masks.size > 0:
                hours_masks = np.vstack((hours_masks, np.logical_and(hour_meta <= hours, hours < data_metas[0][idx + 1])))
            else:
                hours_masks = np.logical_and(hour_meta <= hours, hours < data_metas[0][idx + 1])
        else:
            if hours_masks.size > 0:
                hours_masks = np.vstack((hours_masks, hour_meta <= hours))
            else:
                hours_masks = hour_meta >= hours

    days_masks = np.array([])
    days = np.unique(days_midnight)
    for idx, day in np.ndenumerate(days):
        idx = idx[0]
        if idx < days.size - 1:
            if days_masks.size > 0:
                days_masks = np.vstack(
                    (days_masks, np.logical_and(day <= fecha, fecha < days[idx + 1])))
            else:
                days_masks = np.logical_and(day <= fecha, fecha < days[idx + 1])
        else:
            if days_masks.size > 0:
                days_masks = np.vstack((days_masks, day <= fecha))
            else:
                days_masks = day >= fecha

    days_masks = days_masks if days_masks.ndim > 1 else np.array([days_masks])
    day_count = 0
    table = np.array([])
    for day_mask in days_masks:
        row = np.array([days[day_count]])
        for hour_mask in hours_masks:
            row = np.append(row, np.sum(peso[np.logical_and(day_mask, hour_mask)]))
        row = np.append(row, np.sum(row[2:])) if not_start_day else np.append(row, np.sum(row[1:]))
        table = np.vstack((table, row)) if table.size > 0 else row
        day_count += 1
    dict_data = {'table': table.tolist(), 'star_day_add': bool(not_start_day)}
    return dict_data


@api.get("/download")
async def api_download_file():
    if not os.path.exists(Globs.filePathMeasurements):
        return {"Error": "File not found"}
    return FileResponse(Globs.filePathMeasurements, media_type='application/octet-stream', filename=filePathMeasurements)


@api.post("/upload")
async def api_upload_file(file: UploadFile = File(...)):
    file_path = Globs.filePathMeasurements  # Definimos la ruta y el nombre del archivo en el disco duro
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(4096):
            buffer.write(chunk)
    return "Archivo binario guardado con éxito"
