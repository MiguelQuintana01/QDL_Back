from fastapi import FastAPI

from src.ftp.api import api as ftp_api
from src.settings.api import api as settings_api
from src.weights.api import api as weights_api

app = FastAPI()

app.include_router(ftp_api, prefix="/ftp")
app.include_router(settings_api, prefix="/settings")
app.include_router(weights_api, prefix="/weights")
