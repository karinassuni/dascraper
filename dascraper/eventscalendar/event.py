import dateutil.parser
import logging
import pytz
from collections import OrderedDict
from dascraper.utility import clean_time
from lxml import etree


def parse(html):
    root = etree.HTML(html)
    EVENT_FIELDS = ("description", "date", "time", "location", "sponsor")

    event = {}
    event["name"] = parse.name(root)[0]

    logging.info("Parsing calendar event: {}...".format(event["name"]))

    for field in EVENT_FIELDS:
        try:
            event[field] = root.xpath(
                '//td[contains(., "{}")]/following-sibling::*/text()'
                # The raw fields in HTML are capitalized
                .format(field.capitalize())
            )[0]
        except IndexError:
            logging.debug("'{name}' has no {field}"
                            .format(name=event["name"], field=field))
            event[field] = ''

    logging.info("Finished parsing calendar event: {}".format(event["name"]))
    return clean(event)


parse.name = etree.XPath(
    '//div[@id="cal_div_obj"]/h2/text()'
)


def clean(event):
    for field, value in event.items():
        event[field] = value.strip()

    try:
        start_time, end_time = event["time"].split('-')
    # Not all events have end times; if not, equate to start_time to produce a
    # valid DateTime for here and for clients
    except ValueError:
        start_time = end_time = event["time"]

    event["start"], event["end"] = tuple(
        dateutil.parser.parse(
            event["date"]
            + ' '
            + clean_time.meridiem(t)
        )
        .replace(tzinfo=pytz.timezone("US/Pacific"))
        .isoformat()
        for t in (start_time, end_time)
    )

    # Normalize key order and purge intermediary keys
    order = ("name", "description", "location", "sponsor", "start", "end")
    ordered_event = OrderedDict()
    for key in order:
        # Rename "sponsor" field to "organizationName"
        if key == "sponsor":
            ordered_event["organizationName"] = event["sponsor"]
        else:
            ordered_event[key] = event[key]

    return apply_rules(ordered_event)

def apply_rules(event):
    # Transfer events don't have a sponsor field
    if "UC" in event["name"] \
    or "Transfer Center" in event["location"].capitalize():
        event["organization"] = "Transfer Center"

    return event

