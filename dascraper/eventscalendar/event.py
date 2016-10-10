import logging
import re
from dascraper.utility.clean_time import to_utc_datetime
from lxml import etree


def parse(html):
    root = etree.HTML(html)
    EVENT_FIELDS = ("description", "date", "time", "location", "sponsor")

    event = {}
    event["name"] = parse.name(root)[0]

    logging.info("Parsing calendar event: {}...".format(event["name"]))

    for field in EVENT_FIELDS:
        field_value_nodes = root.xpath(
            '//td[contains(., "{}")]/following-sibling::td/node()'
            # The raw fields in HTML are capitalized
            .format(field.capitalize())
        )
        if not field_value_nodes:
            logging.debug("'{name}' has no {field}"
                            .format(name=event["name"], field=field))
            event[field] = ''
        elif field == "description":
            event["description"] = ''.join([
                el.values()[0] if isinstance(el, etree._Element)
                else el
                for el in field_value_nodes
                if isinstance(el, str)
                or (isinstance(el, etree._Element) and el.values() != [])
            ])
        else:
            event[field] = field_value_nodes[0]

    logging.info("Finished parsing calendar event: {}".format(event["name"]))

    return clean(event)


parse.name = etree.XPath(
    '//div[@id="cal_div_obj"]/h2/text()'
)


def clean(event):
    for field, value in event.items():
        event[field] = value.strip()

    event["name"], event["sponsor"] = tuple(
        # Firebase does not allow these characters in keys
        re.sub('[$#[\].]', '', key)
        for key in (event["name"], event["sponsor"])
    )

    event["description"] = event["description"].replace('\r\n', '\n')

    try:
        start_time, end_time = event["time"].split('-')
    # Not all events have end times; if not, equate to start_time to produce a
    # valid DateTime for here and for clients
    except ValueError:
        start_time = end_time = event["time"]

    event["start"], event["end"] = tuple(
        to_utc_datetime(event["date"], t).isoformat()
        for t in (start_time, end_time)
    )

    # Besides from this source, Events usually have multiple organizations
    sponsor = event.pop("sponsor")
    if sponsor != '':
        event[sponsor] = True

    # "start" and "end" found; raw "time" no longer needed
    event.pop("time", None)

    # "date" already incorporated into "start" and "end"
    event.pop("date", None)

    return apply_rules(event)


def apply_rules(event):
    # Transfer events don't have a sponsor field
    if "UC" in event["name"] \
    or "Transfer Center" in event["location"].capitalize():
        event["Transfer Center"] = True

    return event

