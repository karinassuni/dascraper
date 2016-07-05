import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from . import clean
import json

BASE_URL = "https://www.deanza.edu/eventscalendar/"

def find_calendar_events(calendar_html):
    calendar_soup = BeautifulSoup(calendar_html, "lxml")
    events = []
    calendar = calendar_soup.find("table", class_="main")
    # Skip the first tr, which is the header
    for tr in calendar.find_all("tr")[1:]:
        for td in tr.find_all("td"):
            for a in td.find_all("a"):
                # "class" is a special multi-valued attribute, so it's contained in a list
                if a["class"][0] == "entry":
                    r = requests.get(BASE_URL + a["href"])
                    events.append(parse_event_page(r.text))

    if find_calendar_events.this_month is True:
        find_calendar_events.this_month = False
        NEXT_MONTH = BASE_URL + calendar_soup.find(id="nextmonth").caption.a["href"]
        r = requests.get(NEXT_MONTH)
        return events + find_calendar_events(r.text)
    else:
        return events
# Equivalent to a static local variable in C++--the value of this attribute is preserved
# between function calls
find_calendar_events.this_month = True

def parse_event_page(event_html):
    event_soup = BeautifulSoup(event_html, "lxml")
    FIELD_ROWS = ["description", "date", "time", "location", "sponsor"]
    event = {
        "name": event_soup.find(id="cal_div_obj").h2.get_text().strip(),
        "source": "DA Calendar"
    }

    for tr in event_soup.find("table").find_all("tr"):
        field_name = tr.contents[0].get_text().lower().strip()[:-1]
        if field_name in FIELD_ROWS:
            field_value = tr.contents[1].get_text().strip()
            if field_name == "date":
                event["date"] = datetime.strptime(field_value, "%A, %B %d, %Y").date().isoformat()
            elif field_name == "time":
                event["start_time"] = clean.time(field_value.split('-')[0])
                event["end_time"] = clean.time(field_value.split('-')[1])
            else:
                event[field_name] = field_value

    return event

def main():
    THIS_MONTH = BASE_URL + "month.php"
    logging.debug("Requesting {}...".format(THIS_MONTH))

    r = requests.get(THIS_MONTH)
    with open("calendar.html", 'w') as outfile:
        outfile.write(r.text)
    logging.debug("Downloaded this month's calendar.")

    with open("calendarevents.json", 'w') as outfile:
        json.dump(find_calendar_events(r.text), outfile)

    logging.debug("Parsing complete! Saved to calendar_events.json.")

if __name__ == "__main__":
    main()
