import numpy as np

from src.file.file import get_all_measures


def get_weight(start: int, end: int):
    history_dates, history_weights = get_all_measures()
    mask_of_period = np.logical_and(history_dates >= start, history_dates <= end)
    history_dates = history_dates[mask_of_period]
    history_weights = history_weights[mask_of_period]
    return history_dates, history_weights
