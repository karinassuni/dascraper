import dascraper.utility.requests as requests
import datetime
import json
import logging
from lxml import etree
from . import event


BASE_URL = "https://www.deanza.edu/eventscalendar/"


def crawl(html, link_handler):
    root = etree.HTML(html)

    month = crawl.month(root)[0]
    logging.info("Crawling the {} calendar...".format(month))

    for e in crawl.event_parameters(root):
        link_handler(BASE_URL + e)

    logging.info("Finished crawling the {} calendar".format(month))


# PHP filename included
crawl.event_parameters = etree.XPath(
    '//a[@class="entry"]/attribute::href'
)

crawl.month = etree.XPath(
    '//span[@class="date"]/text()'
)


@requests.get
def parse(response):
    events = {}

    def event_url_handler(url):
        r = requests.attempt("GET", url)
        try:
            e = event.parse(r.content)
        except ValueError:
            return

        start_date = e["start"][:e["start"].index('T')]
        key = start_date + '|' + e.pop("name")

        events[key] = e

    crawl(response.content, event_url_handler)

    return events


def merge_two_dicts(a, b):
    c = a.copy()
    c.update(b)
    return c


def main():
    # Defaults to getting this month's calendar
    MONTH_PAGE = BASE_URL + "month.php"

    events_this_month = parse(MONTH_PAGE)

    today = datetime.date.today()
    next_month_query = {"year": today.year, "month": today.month + 1}
    events_next_month = parse(MONTH_PAGE, next_month_query)
    events = merge_two_dicts(events_this_month, events_next_month)

    with open("calendarevents.json", 'w') as o:
        json.dump(events, o,
            indent=4, separators=(',', ': '))

    logging.info("Parsing complete! Saved to calendarevents.json")


if __name__ == "__main__":
    main()
