import re
import datetime


def ptime(time):
    clean_time = ''
    hhmm = re.search("\d{1,2}:\d{2}", time).group(0)
    if 'a' in time.lower():
        clean_time = hhmm + "AM"
    elif 'p' in time.lower():
        clean_time = hhmm + "PM"

    return clean_time


def iso_time(time):
    return (
        datetime.datetime
        .strptime(ptime(time), "%I:%M%p")
        .time()
        .isoformat()
    )
