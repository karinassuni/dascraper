import datetime
import logging
import json
import requests
from bs4 import BeautifulSoup
from .clean import iso_time
from collections import namedtuple

BASE_URL = "https://www.deanza.edu/eventscalendar/"

def parse_calendar(html):
    calendar_soup = BeautifulSoup(html, "lxml")
    calendar = calendar_soup.find("table", class_="main")
    START_ROW = 1
    events = []

    for tr in calendar.find_all("tr")[START_ROW:]:
        for td in tr.find_all("td"):
            for a in td.find_all("a"):
                # "class" is a special multi-valued attribute, so it's contained in a list
                if a["class"][0] == "entry":
                    r = requests.get(BASE_URL + a["href"])
                    events.append(parse_event(r.text))

    return events

def parse_event(html):
    event_soup = BeautifulSoup(html, "lxml")
    DESIRED_ROWS = ["description", "date", "time", "location", "sponsor"]

    event = {
        "name": event_soup.find(id="cal_div_obj").h2.get_text().strip(),
        "source": "DA Calendar"
    }

    for tr in event_soup.find("table").find_all("tr"):
        raw_field_name = tr.contents[0].get_text()
        field_name = ''.join(c for c in raw_field_name.lower() if c.isalpha())
        if field_name in DESIRED_ROWS:
            field_value = tr.contents[1].get_text().strip()
            if field_name == "date":
                event["date"] = (
                    datetime.datetime
                    .strptime(field_value, "%A, %B %d, %Y")
                    .date()
                    .isoformat()
                )
            elif field_name == "time":
                event["start_time"] = iso_time(field_value.split('-')[0])
                event["end_time"] = iso_time(field_value.split('-')[1])
            else:
                event[field_name] = field_value

    return event

def extract_calendar_events(url, *data):
    logging.debug("Requesting {}...".format(url))
    if data:
        r = requests.get(url, data)
    else:
        r = requests.get(url)
    logging.debug("Downloaded {}.".format(url))

    return parse_calendar(r.text)

def main():
    MONTH_SCRIPT = BASE_URL + "month.php"

    this_month_events = extract_calendar_events(MONTH_SCRIPT)

    today = datetime.date.today()
    next_month_query = {"year": today.year, "month": today.month + 1}
    next_month_events = extract_calendar_events(MONTH_SCRIPT, next_month_query)

    with open("calendarevents.json", 'w') as outfile:
        json.dump(this_month_events + next_month_events, outfile)

    logging.debug("Parsing complete! Saved to calendarevents.json.")

if __name__ == "__main__":
    main()
