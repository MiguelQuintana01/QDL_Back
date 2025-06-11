import json
import os

from src.variables import Globs


def save_dict_as_json(dictionary, filename):
    """
    Save a dictionary to a JSON file.

    :param dictionary: Dictionary to save.
    :param filename: Name of the file where the dictionary will be saved.
    """
    with open(filename, 'w') as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)
    print(f"Dictionary saved to {filename}.")


def load_json_as_dict(filename):
    """
    Read a JSON file and convert it to a dictionary. If the file does not exist,
    return an empty dictionary.

    :param filename: Name of the JSON file to read.
    :return: Dictionary obtained from the JSON file, or an empty dictionary if the file does not exist.
    """
    if not os.path.isfile(filename):
        print(f"File {filename} does not exist. Returning empty dictionary.")
        return {}

    with open(filename, 'r') as file:
        dictionary = json.load(file)
    print(f"Dictionary loaded from {filename}.")
    return dictionary


def verify_settings_exit():
    if not os.path.isfile(Globs.fileSettings):
        settings_default = {
            "ftp_server": "",
            "ftp_port": 21,
            "username": "",
            "password": "",
            "gmt": ""
        }
        save_dict_as_json(settings_default, Globs.fileSettings)


def get_settings():
    return load_json_as_dict(Globs.fileSettings)


verify_settings_exit()
settings = load_json_as_dict(Globs.fileSettings)
