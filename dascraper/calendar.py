import dascraper.calendarevents as calendarevents
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

    for week in calendar.find_all("tr")[START_ROW:]:
        for day in week.find_all("td"):
            for link in day.find_all("a"):
                # "class" is a special multi-valued attribute, so it's contained in a list
                if link["class"][0] == "entry":
                    r = requests.get(BASE_URL + link["href"])
                    events.append(calendarevents.parse(r.text))

    return events


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

    with open("calendarevents.json", 'w') as o:
        json.dump(events_this_month + events_next_month, o,
            sort_keys=True, indent=4, separators=(',', ': '))

    logging.debug("Parsing complete! Saved to calendarevents.json")


if __name__ == "__main__":
    main()
