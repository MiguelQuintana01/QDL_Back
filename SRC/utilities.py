from datetime import datetime


def midnight() -> datetime:
    # Get the current date and time
    now = datetime.now()
    # Create a datetime object for midnight of the current date
    today_midnight = datetime(now.year, now.month, now.day)
    return today_midnight
