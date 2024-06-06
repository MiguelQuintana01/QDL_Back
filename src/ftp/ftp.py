from datetime import datetime, timedelta
from ftplib import FTP, error_perm

from src.utilities import get_gmt

file_path = "files/indicadores.csv"
local_file_path = "indicadores.csv"
directory = "/files"


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
    if not ftp_file_exists(ftp_server, ftp_port, username, password):
        print("The file dont exist.")
        return datetime(2200, 1, 1)

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

        return file_date_datetime + timedelta(hours=get_gmt())

    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        return datetime(2200, 1, 1)


def ftp_file_exists(ftp_server: str, ftp_port: int, username: str, password: str, **kwargs):
    ftp = None
    filename = local_file_path

    if not filename:
        raise ValueError("The 'filename' argument is required.")

    try:
        # Connect to the FTP server on the specified port
        ftp = FTP()
        ftp.connect(host=ftp_server, port=ftp_port)
        ftp.login(user=username, passwd=password)

        # Change to the desired directory
        ftp.cwd(directory)

        # Try to get the file size; if it fails, it means the file doesn't exist
        try:
            ftp.size(filename)
            return True  # File exists
        except error_perm as e:
            # Responds with an error if the file does not exist or there's a permission issue
            if str(e).startswith('550'):
                return False  # File doesn't exist
            else:
                raise  # Other FTP errors

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        # Make sure to close the connection
        if ftp:
            ftp.quit()
