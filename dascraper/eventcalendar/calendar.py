import datetime
import json
import logging
import os
import requests
from dascraper.eventcalendar import event
from lxml import etree


BASE_URL = "https://www.deanza.edu/eventscalendar/"


def crawl(html, link_handler):

    root = etree.HTML(html)

    month = crawl.find_month(root)[0]
    logging.info("***** Crawling the {} calendar... *****".format(month))

    for e in crawl.find_event_path_components(root):
        link_handler(BASE_URL + e)

    logging.info("***** Finished crawling the {} calendar... *****".format(month))


crawl.find_event_path_components = etree.XPath(
    '//a[@class="entry"]/attribute::href'
)
crawl.find_month = etree.XPath(
    '//span[@class="date"]/text()'
)


def get_request(func):
    def decorator(*args):
        try:
            r = requests.get(*args)
        except requests.exceptions.RequestException:
            logging.exception("Something went wrong with the request! Exiting...")
            sys.exit(1)
        else:
            return func(r.content)
    return decorator


@get_request
def parse(html):
    events = []

    def event_url_handler(url):
        r = requests.get(url)
        events.append(event.parse(r.content))

    crawl(html, event_url_handler)

    return events


def main():
    # Defaults to getting this month's calendar
    MONTH_PAGE = BASE_URL + "month.php"

    events_this_month = parse(MONTH_PAGE)

    today = datetime.date.today()
    next_month_query = {"year": today.year, "month": today.month + 1}
    events_next_month = parse(MONTH_PAGE, next_month_query)

    try:
        with open(os.path.join(
            os.environ.get("OPENSHIFT_DATA_DIR"), "json/", "calendarevents.json"), 'w') as o:
                json.dump(events_this_month + events_next_month, o,
                    sort_keys=True, indent=4, separators=(',', ': '))

    except KeyError:
        logging.error("SOMETHING IS WRONG WITH $OPENSHIFT_DATA_DIR, could not "
                      "save calendarevents.json!")

    else:
        logging.info("Parsing complete! Saved to calendarevents.json")


if __name__ == "__main__":
    main()
