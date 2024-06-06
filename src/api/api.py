import os

import fastapi.staticfiles
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, HTMLResponse

from src.ftp.api import api as ftp_api
from src.settings.api import api as settings_api
from src.variables import prefix
from src.weights.api import api as weights_api
from src.file.api import api as file_api
from src.meta.api import api as meta_api

app = FastAPI()

# Example CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ftp_api, prefix=prefix+"/ftp")
app.include_router(settings_api, prefix=prefix+"/settings")
app.include_router(weights_api, prefix=prefix+"/weights")
app.include_router(file_api, prefix=prefix+"/files")
app.include_router(meta_api, prefix=prefix+"/metas")

actual_dir = os.getcwd()
app.mount("/", fastapi.staticfiles.StaticFiles(directory=os.path.abspath(r".\front\qdl-angular\browser"),
                                               html=True), name='static')

@app.middleware("http")
async def redirect_to_index(request: Request, call_next):
    if not request.url.path.startswith("/api/"):
        response = await call_next(request)
        if response.status_code == 404:
            return HTMLResponse(content=open(r"D:\Downloads\git\QDL_Back\front\qdl-angular\browser"+f"/index.html", "r").read(), status_code=200)
        return response
    else:
        return await call_next(request)