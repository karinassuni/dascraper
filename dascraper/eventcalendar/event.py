import datetime
import logging
from dascraper import cleantime
from lxml import etree


def parse(html):
    root = etree.HTML(html)
    EVENT_FIELDS = ("description", "date", "time", "location", "sponsor")

    event = {}
    event["name"] = parse.find_name(root)[0]
    event["source"] = "DA Calendar"

    logging.debug("Parsing calendar event: {}...".format(event["name"]))

    for f in EVENT_FIELDS:
        event[f] = root.xpath(
            '//td[contains(., "{}")]/following-sibling::*/text()'
            # The raw fields in HTML are capitalized
            .format(f.capitalize())
        )[0]

    logging.debug("Finished parsing calendar event: {}".format(event["name"]))
    return clean(event)

parse.find_name = etree.XPath(
    '//div[@id="cal_div_obj"]/h2/text()'
)


def clean(event):

    for field, value in event.items():
        event[field] = value.strip()

    event["date"] = (
        datetime.datetime
        .strptime(event["date"], "%A, %B %d, %Y")
        .date()
        .isoformat()
    )

    event["start_time"] = cleantime.iso(
        event["time"]
        .split('-')[0]
    )
    event["end_time"] = cleantime.iso(
        event["time"]
        .split('-')[1]
    )

    # start_time and end_time found; raw "time" no longer needed
    event.pop("time", None)

    return event
