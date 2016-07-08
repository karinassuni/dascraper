import datetime
import logging
from bs4 import BeautifulSoup
from . import cleantime


def parse(html):
    logging.info("Parsing calendar event:")

    soup = BeautifulSoup(html, "lxml")
    EVENT_FIELDS = ("description", "date", "time", "location", "sponsor")

    event = {
        "name": soup.find(id="cal_div_obj").h2.get_text().strip(),
        "source": "DA Calendar"
    }
    logging.debug(event["name"])

    for row in soup.find("table").find_all("tr"):
        raw_row_name = row.contents[0].get_text()
        row_name = ''.join(c for c in raw_row_name.lower() if c.isalpha())
        if row_name in EVENT_FIELDS:
            value = row.contents[1].get_text().strip()
            event[row_name] = value

    logging.info("Finished parsing {}".format(event["name"]))
    return clean(event)


def clean(event):
    clean_event = event
    clean_event["date"] = (
        datetime.datetime
        .strptime(event["date"], "%A, %B %d, %Y")
        .date()
        .isoformat()
    )
    clean_event["start_time"] = cleantime.iso(event["time"].split('-')[0])
    clean_event["end_time"] = cleantime.iso(event["time"].split('-')[1])

    # start_time and end_time found; raw "time" no longer needed
    clean_event.pop("time", None)

    return clean_event
