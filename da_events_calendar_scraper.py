import sys
import requests
from bs4 import BeautifulSoup
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
    EVENT_FIELDS = ["Description:", "Date:", "Time:", "Location:", "Sponsor:"]
    event = {
        "name": event_soup.find(id="cal_div_obj").h2.get_text(),
        "source": "DA Calendar"
    }

    for tr in event_soup.find("table").find_all("tr"):
        field_name = tr.contents[0].get_text().strip()
        if field_name in EVENT_FIELDS:
            field_value = tr.contents[1].get_text().strip()
            event[field_name[:-1].lower()] = field_value

    return event

def main():
    def download_calendar_html():
        THIS_MONTH = BASE_URL + "month.php"
        print "Requesting {}...".format(THIS_MONTH)
        r = requests.get(THIS_MONTH)
        with open("calendar.html", 'w') as outfile:
            outfile.write(r.text)
        print "This month's calendar downloaded."

        return r.text

    def save_events_json(events):
        with open("calendar_events.json", 'w') as outfile:
            json.dump(events, outfile)

    if len(sys.argv) == 2:
        save_events_json(find_calendar_events(sys.argv[1]))
    elif len(sys.argv) == 1:
        save_events_json(find_calendar_events(download_calendar_html()))
    else:
        print "Invalid argument list. Exiting..."
        sys.exit(2)
    print "Parsing complete! Saved to calendar_events.json."

if __name__ == "__main__":
    main()
