import re
import datetime

def clean_time(time):
    hhmm = re.search("\d{1,2}:\d{2}", time).group(0)
    if 'a' in time.lower():
        time = hhmm + "AM"
    elif 'p' in time.lower():
        time = hhmm + "PM"

    return time

def iso_time(time):
    return (
        datetime.datetime
        .strptime(clean_time(time), "%I:%M%p")
        .time()
        .isoformat()
    )
