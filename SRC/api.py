from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse

from SRC.ftp.ftp import ftp_download_file, ftp_delete_file, ftp_get_creation_date

app = FastAPI()


@app.post("/download-ftp-file/")
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


@app.delete("/delete-ftp-file")
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


@app.get("/weights/ftp/date")
async def get_date_creation(
        ftp_server: str = Form(...),
        ftp_port: int = Form(default=21),  # Puerto predeterminado de FTP es 21
        username: str = Form(default=""),
        password: str = Form(default="")
):
    try:
        file_date = ftp_get_creation_date(ftp_server, ftp_port, username, password)
        print(file_date.time())
        return file_date.isoformat()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
