from fastapi import FastAPI

from SRC.ftp.api import api as ftp_api
from SRC.settings.api import api as settings_api

app = FastAPI()

app.include_router(ftp_api, prefix="/ftp")
app.include_router(settings_api, prefix="/settings")
