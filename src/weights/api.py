import json

from fastapi import APIRouter, Form

from src.weights.weight import get_weight

api = APIRouter()


@api.get("")
def get_weight_api(start: int = Form(default=0), end: int = Form(default=4102444800)):
    history_dates, history_weights = get_weight(start, end)
    dict_measures = {"fecha": [date_value for date_value in history_dates],
                     "peso": [history_value for history_value in history_weights]}
    return dict_measures
