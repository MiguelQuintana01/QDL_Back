import json
import os

from SRC.variables import fileSettings


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
    if not os.path.exists(filename):
        print(f"File {filename} does not exist. Returning empty dictionary.")
        return {}

    with open(filename, 'r') as file:
        dictionary = json.load(file)
    print(f"Dictionary loaded from {filename}.")
    return dictionary


settings = load_json_as_dict(fileSettings)
