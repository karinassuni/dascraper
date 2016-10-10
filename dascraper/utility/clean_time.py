import datetime
import dateutil.parser
import re
import pytz


def meridiem(time):
    """
    Returns time with a normalized meridiem
    >>> period("5:30 pom ")
        "5:30PM"
    """

    try:
        hhmm = re.search("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]", time.lstrip()).group(0)
    except AttributeError as error:
        raise ValueError("''{}' is not a valid 12-hour time".format(time)) from error

    # Convert 24 hour times to meridiem times
    hour = int(hhmm[:hhmm.index(':')])
    if hour == 0:
        return "12:00AM"
    elif hour > 12 and hour < 24:
        minute = hhmm[hhmm.index(':') + 1:]
        return str(hour % 12) + ':' + minute + "PM"

    time = time.lower()

    if 'a' in time:
        return hhmm + "AM"
    elif 'p' in time:
        return hhmm + "PM"
    else:
        if hhmm[0] == '0':
            return hhmm + "AM"
        else:
            raise ValueError("The meridiem of '{}' cannot be determined".format(time))


def isoformat(time):
    """
    Returns time in ISO format
    >>> iso("5:30 pom ")
        "17:30:00"
    """

    try:
        struct_time = datetime.datetime.strptime(meridiem(time), "%I:%M%p")
    except ValueError:
        try:
            # Try 24-hour time
            struct_time = datetime.datetime.strptime(meridiem(time), "%H:%M")
        except ValueError:
            raise

    return struct_time.time().isoformat()


def to_utc_datetime(date, time):
    original_tz = pytz.timezone("US/Pacific")
    return original_tz.localize(
        dateutil.parser.parse(
            date
            + ' '
            + time
        )
    )
