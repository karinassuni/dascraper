import requests
from bs4 import BeautifulSoup
from lxml import etree
import json

def find_calendar_events(url):
    print "Requesting {}...".format(url)
    r = requests.get(url)
    with open("calendar.html", 'w') as outfile:
        outfile.write(r.text):w
        K
    print "Calendar downloaded. Parsing..."
    calendar_soup = BeautifulSoup(r.text, "html.parser")

    events = []
    calendar_body = calendar_soup.find("table", class_="main")
    # skip the first tr, which is the header
    for tr in calendar_body.find_all("tr")[1:]:
        for td in tr.find_all("td"):
            for a in td.find_all("a"):
                if a["class"] == "entry":
                    events.append(parse_event_page(BASE_CALENDAR_URL + a["href"]))

    return events

def parse_event_page(url):
    r = requests.get(url)
    event_soup = BeautifulSoup(r.text, "html.parser")
    EVENT_FIELDS = ["Description", "Date", "Time", "Location", "Sponsor"]
    event = {}

    event["name"] = event_soup.find(id="cal_div_obj").h2.get_text()

    for tr in event_soup.find("tbody"):
        field_name = tr.contents[0].get_text()
        if field_name in EVENT_FIELDS:
            field_value = tr.contents[1].get_text()
            event[field_name.lower()] = field_value

    return event

if __name__ == "__main__"::w:w
K:w


    BASE_URL = "https://www.deanza.edu/eventscalendar/"

    with open("calendar_events.json", 'w') as outfile:
        json.dump(find_calendar_events(BASE_URL + "month.php"), outfile)
    print "Parsing complete! Saved to calendar_events.json."
