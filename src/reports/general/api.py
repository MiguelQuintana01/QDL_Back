import datetime

import pandas as pd
from fastapi import APIRouter

from src.file.file import download_csv
from src.utilities import datetime_to_unix

api = APIRouter()


@api.get("")
def get_data() -> dict:
    general_report = {
        "Fecha": [
            datetime_to_unix(datetime.datetime(2025, 1, 11)),
            datetime_to_unix(datetime.datetime(2025, 1, 11)),
            datetime_to_unix(datetime.datetime(2025, 1, 11))
        ],
        "Orden": ["773", "777", "780"],
        "SKU": ["QCA-BFP", "QB-VMC", "QB-VMC"],
        "Lote": ["008-18", "008-21", "013-1B"],
        "Cajas": ["45", "36", "26"],
        "Piezas": ["180", "288", "208"],
        "Peso": ["392.205", "713.748", "512.268"],
        "Hora Primera Caja": [
            datetime_to_unix(datetime.datetime(2025, 1, 11, 6, 45)),
            datetime_to_unix(datetime.datetime(2025, 1, 11, 13, 29)),
            datetime_to_unix(datetime.datetime(2025, 1, 11, 13, 48))
        ],
        "Hora Ultima Caja": [
            datetime_to_unix(datetime.datetime(2025, 1, 11, 6, 56)),
            datetime_to_unix(datetime.datetime(2025, 1, 11, 13, 47)),
            datetime_to_unix(datetime.datetime(2025, 1, 11, 14, 2))
        ]
    }
    return general_report

@api.get('/csv')
def get_csv() -> dict:
    return download_csv(pd.DataFrame(get_data()))
