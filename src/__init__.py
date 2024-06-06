import threading
import time

import src.ftp.api
from src.api.api import app
from src.file.file import verify_ftp_file


def run_scheduled_tasks():
    while True:
        try:
            verify_ftp_file()
        except Exception as e:
            pass
        finally:
            time.sleep(60)


if __name__ == "__main__":

    thread = threading.Thread(target=run_scheduled_tasks)
    thread.daemon = True
    thread.start()
    verify_ftp_file()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
