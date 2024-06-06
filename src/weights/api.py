from fastapi import APIRouter, Form

from src.file.file import download_csv_weights, get_weight

api = APIRouter()


@api.post("")
def get_weight_api(start: int = Form(default=0), end: int = Form(default=4102444800)):
    history_dates, history_weights = get_weight(start, end)
    dict_measures = {"fecha": history_dates.tolist(),
                     "peso": history_weights.tolist()}
    return dict_measures


@api.post("/download-csv")
def download_csv(start: int = Form(0), end: int = Form(4102444800), gmt: int = Form(0)):
    return download_csv_weights(start, end, gmt)
