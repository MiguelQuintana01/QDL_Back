from datetime import datetime
from ftplib import FTP

file_path = "files/indicadores.csv"
local_file_path = "indicadores.csv"


def ftp_download_file(ftp_server: str, ftp_port: int, username: str, password: str, **kwargs) -> str:
    global file_path
    global local_file_path

    try:
        # Conexión al servidor FTP
        print(f"Conectando al servidor FTP: {ftp_server}:{ftp_port}")
        ftp = FTP()
        ftp.connect(ftp_server, ftp_port)
        ftp.login(user=username, passwd=password)
        print(f"Conectado al servidor FTP: {ftp_server}:{ftp_port}")

        # Descarga del archivo
        with open(local_file_path, "wb") as local_file:
            ftp.retrbinary(f"RETR {file_path}", local_file.write)

        # Cierre de la sesión FTP
        ftp.quit()
        print(f"Archivo {file_path} descargado exitosamente")

        return local_file_path

    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        raise Exception(f"Error al descargar el archivo: {error_message}")


def ftp_delete_file(ftp_server: str, ftp_port: int, username: str, password: str, **kwargs) -> str:
    global file_path

    try:
        # Conexión al servidor FTP
        print(f"Conectando al servidor FTP: {ftp_server}:{ftp_port}")
        ftp = FTP()
        ftp.connect(ftp_server, ftp_port)
        ftp.login(user=username, passwd=password)
        print(f"Conectado al servidor FTP: {ftp_server}:{ftp_port}")

        # Eliminación del archivo
        ftp.delete(file_path)
        print(f"Archivo {file_path} eliminado exitosamente")

        # Cierre de la sesión FTP
        ftp.quit()

        return f"Archivo {file_path} eliminado exitosamente"

    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        raise Exception(f"Error al eliminar el archivo: {error_message}")


def ftp_get_creation_date(ftp_server: str, ftp_port: int, username: str, password: str, **kwargs) -> datetime:
    global file_path
    try:
        # Conexión al servidor FTP
        print(f"Conectando al servidor FTP: {ftp_server}:{ftp_port}")
        ftp = FTP()
        ftp.connect(ftp_server, ftp_port)
        ftp.login(user=username, passwd=password)
        print(f"Conectado al servidor FTP: {ftp_server}:{ftp_port}")

        # Obtención de la fecha de modificación del archivo
        response = ftp.sendcmd(f"MDTM {file_path}")
        if response.startswith("213"):
            file_date = response[4:]
            formatted_date = (f"{file_date[:4]}-{file_date[4:6]}-{file_date[6:8]}T"
                              f"{file_date[8:10]}:{file_date[10:12]}:{file_date[12:14]}")
            file_date_datetime = datetime.fromisoformat(formatted_date)
            print(f"Fecha de modificación del archivo {file_path}: {formatted_date}")
        else:
            raise Exception("No se pudo obtener la fecha de modificación del archivo")

        # Cierre de la sesión FTP
        ftp.quit()

        return file_date_datetime

    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        raise Exception(f"Error al obtener la fecha del archivo: {error_message}")
