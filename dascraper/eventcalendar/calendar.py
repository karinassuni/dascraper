import datetime
import json
import logging
import requests
from bs4 import BeautifulSoup
from . import event


BASE_URL = "https://www.deanza.edu/eventscalendar/"


def crawl(html, link_handler):
    logging.info("Crawling calendar...")

    soup = BeautifulSoup(html, "lxml")
    calendar = soup.find("table", class_="main")
    START_ROW = 1

    for week in calendar.find_all("tr")[START_ROW:]:
        for day in week.find_all("td"):
            for link in day.find_all("a"):
                # "class" is a special multi-valued attribute, so it's contained in a list
                if link["class"][0] == "entry":
                    link_handler(BASE_URL + link["href"])

    month = soup.find("span", class_="date").text
    logging.info("Finished crawling the {} calendar".format(month))



def parse(html):
    events = []

    def event_url_handler(url):
        r = requests.get(url)
        events.append(event.parse(r.text))

    crawl(html, event_url_handler)

    return events


def main():
    # Defaults to getting this month's calendar
    MONTH_SCRIPT = BASE_URL + "month.php"

    try:
        r = requests.get(MONTH_SCRIPT)
    except requests.exceptions.RequestException:
        logging.exception("Something went wrong with the request! Exiting...")
        sys.exit(1)
    else:
        events_this_month = parse(r.text)

    today = datetime.date.today()
    next_month_query = {"year": today.year, "month": today.month + 1}
    try:
        r = requests.get(MONTH_SCRIPT, next_month_query)
    except requests.exceptions.RequestException:
        logging.exception("Something went wrong with the request! Exiting...")
        sys.exit(1)
    else:
        events_next_month = parse(r.text)

    with open("calendarevents.json", 'w') as o:
        json.dump(events_this_month + events_next_month, o,
            sort_keys=True, indent=4, separators=(',', ': '))

    logging.info("Parsing complete! Saved to calendarevents.json")


if __name__ == "__main__":
    main()
