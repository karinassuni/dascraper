import datetime
import logging
from dascraper.utility import clean_time
from lxml import etree


def parse(html):
    root = etree.HTML(html)
    EVENT_FIELDS = ("description", "date", "time", "location", "sponsor")

    event = {}
    event["name"] = parse.name(root)[0]
    event["source"] = "DA Calendar"

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

    event["date"] = (
        datetime.datetime
        .strptime(event["date"], "%A, %B %d, %Y")
        .date()
        .isoformat()
    )

    event["start_time"] = clean_time.isoformat(
        event["time"]
        .split('-')[0]
    )

    # Not all events have end times
    try:
        event["end_time"] = clean_time.isoformat(
            event["time"]
            .split('-')[1]
        )
    except IndexError:
        event["end_time"] = ''

    # start_time and end_time found; raw "time" no longer needed
    event.pop("time", None)

    return event
