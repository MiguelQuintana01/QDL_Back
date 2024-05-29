from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import FileResponse

from SRC.api.utilities import is_yesterday_date
from SRC.file.file import append_indicadores_history
from SRC.ftp.ftp import ftp_download_file, ftp_delete_file, ftp_get_creation_date
from SRC.settings.settings import settings

api = APIRouter()


@api.get("")
async def download_ftp_file(
        ftp_server: str = Form(...),
        ftp_port: int = Form(default=21),  # Puerto predeterminado de FTP es 21
        username: str = Form(default=""),
        password: str = Form(default="")
):
    try:
        local_file_path = ftp_download_file(ftp_server, ftp_port, username, password)
        return FileResponse(local_file_path, filename="indicadores.csv")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.delete("")
async def erase_ftp_file(
        ftp_server: str = Form(...),
        ftp_port: int = Form(default=21),  # Puerto predeterminado de FTP es 21
        username: str = Form(default=""),
        password: str = Form(default="")
):
    try:
        return ftp_delete_file(ftp_server, ftp_port, username, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.get("/date")
async def get_date_creation(
        ftp_server: str = Form(...),
        ftp_port: int = Form(default=21),  # Puerto predeterminado de FTP es 21
        username: str = Form(default=""),
        password: str = Form(default="")
):
    try:
        file_date = ftp_get_creation_date(ftp_server, ftp_port, username, password)
        print(is_yesterday_date(file_date))
        return file_date.isoformat()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.get("/verify")
async def verify_ftp_file():
    if is_yesterday_date(ftp_get_creation_date(**settings)):
        append_indicadores_history()
