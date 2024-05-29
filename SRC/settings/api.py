from fastapi import APIRouter, HTTPException, Form

from SRC.settings.settings import save_dict_as_json
from SRC.variables import fileSettings

api = APIRouter()


@api.post("")
async def download_ftp_file(
        ftp_server: str = Form(...),
        ftp_port: int = Form(default=21),  # The default port of FTP is 21
        username: str = Form(default=""),
        password: str = Form(default="")
):
    try:
        settings = {'ftp_server': ftp_server, 'ftp_port': ftp_port, 'username': username, 'password': password}
        save_dict_as_json(settings, fileSettings)
        return "Settings updated"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
