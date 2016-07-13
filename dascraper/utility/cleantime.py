import re
import datetime


def period(time):
    """
    Returns time with an ISO-compatible period
    >>> period("5:30 pom ")
        "5:30PM"
    """

    hhmm = re.search("\d{1,2}:\d{2}", time).group(0)
    if 'a' in time.lower():
        time = hhmm + "AM"
    elif 'p' in time.lower():
        time = hhmm + "PM"

    return time


def iso(time):
    """
    Returns time in ISO format
    >>> iso("5:30 pom ")
        "17:30:00"
    """
    return (
        datetime.datetime
        .strptime(period(time), "%I:%M%p")
        .time()
        .isoformat()
    )
