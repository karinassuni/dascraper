import dascraper.cleantime as cleantime
import datetime
import json
import logging
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.deanza.edu/eventscalendar/"


def parse(html):
    soup = BeautifulSoup(html, "lxml")
    calendar = soup.find("table", class_="main")
    START_ROW = 1
    events = []

    for tr in calendar.find_all("tr")[START_ROW:]:
        for td in tr.find_all("td"):
            # Get links to events' pages, where you will parse event data
            for a in td.find_all("a"):
                # "class" is a special multi-valued attribute, so it's contained in a list
                if a["class"][0] == "entry":
                    r = requests.get(BASE_URL + a["href"])
                    events.append(parse_event(r.text))

    return events


def parse_event(html):
    soup = BeautifulSoup(html, "lxml")
    EVENT_FIELDS = ("description", "date", "time", "location", "sponsor")

    event = {
        "name": soup.find(id="cal_div_obj").h2.get_text().strip(),
        "source": "DA Calendar"
    }

    for tr in soup.find("table").find_all("tr"):
        raw_row_name = tr.contents[0].get_text()
        row_name = ''.join(c for c in raw_row_name.lower() if c.isalpha())
        if row_name in EVENT_FIELDS:
            value = tr.contents[1].get_text().strip()
            event[row_name] = value

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


def main():
    MONTH_SCRIPT = BASE_URL + "month.php"

    try:
        events_this_month = parse(requests.get(MONTH_SCRIPT).text)
    except requests.exceptions.RequestException:
        logging.exception("Something went wrong with the request! Exiting...")
        sys.exit(1)

    today = datetime.date.today()
    try:
        next_month_query = {"year": today.year, "month": today.month + 1}
        events_next_month = parse(requests.get(
            MONTH_SCRIPT, next_month_query).text)
    except requests.exceptions.RequestException:
        logging.exception("Something went wrong with the request! Exiting...")
        sys.exit(1)

    with open("calendarevents.json", 'w') as outfile:
        json.dump(events_this_month + events_next_month, outfile, sort_keys=True)

    logging.debug("Parsing complete! Saved to calendarevents.json")


if __name__ == "__main__":
    main()
