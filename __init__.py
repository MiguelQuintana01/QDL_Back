import os
import threading
import time

from src.api.api import app
from src.file.file import verify_csv_file


def run_scheduled_tasks():
    while True:
        try:
            verify_csv_file()
        except Exception as e:
            pass
        finally:
            time.sleep(60)


if __name__ == "__main__":
    actual_dir = os.getcwd()
    print(actual_dir)

    thread = threading.Thread(target=run_scheduled_tasks)
    thread.daemon = True
    thread.start()
    verify_csv_file()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
