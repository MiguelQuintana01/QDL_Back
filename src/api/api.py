import os

import fastapi.staticfiles
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from src.ftp.api import api as ftp_api
from src.settings.api import api as settings_api
from src.variables import Globs
from src.weights.api import api as weights_api
from src.file.api import api as file_api
from src.meta.api import api as meta_api
from src.reports.general.api import api as general_api

app = FastAPI()

# Example CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ftp_api, prefix=Globs.prefix+"/ftp")
app.include_router(settings_api, prefix=Globs.prefix+"/settings")
app.include_router(weights_api, prefix=Globs.prefix+"/weights")
app.include_router(file_api, prefix=Globs.prefix+"/files")
app.include_router(meta_api, prefix=Globs.prefix+"/metas")
app.include_router(general_api, prefix=Globs.prefix+"/general")

actual_dir = os.getcwd()
browser_path = os.path.abspath("front/qdl-18/browser")
app.mount("/", fastapi.staticfiles.StaticFiles(directory=browser_path,
                                               html=True), name='static')


@app.middleware("http")
async def redirect_to_index(request: Request, call_next):
    if not request.url.path.startswith("/api/"):
        response = await call_next(request)
        if response.status_code == 404:
            return HTMLResponse(content=open(browser_path+f"/index.html", "r").read(), status_code=200)
        return response
    else:
        return await call_next(request)
