import datetime
import docx
import logging
import json
import os
from dascraper.clean import iso_time

# Path arguments in os.path are relative to the present working directory
# (the directory from where the module is called), so use the unchanging
# absolute path to the directory containing this file via `__file__`
WORD_DOC = docx.Document(os.path.join(os.path.dirname(__file__), os.path.relpath("res/ClubMeetingsSpring2016.docx")))

def parse():
    START_INDEX = 3
    NAME_INDEX, DAYS_INDEX, DATES_INDEX, TIME_INDEX, LOCATION_INDEX = range(1, 6)
    clubs = []

    logging.debug("Parsing the club spreadsheet...")

    for table in WORD_DOC.tables:
        for row in table.rows[START_INDEX:]:
            club_is_active = bool(row.cells[DATES_INDEX].text.strip())
            if club_is_active:
                club = {
                    "name": row.cells[NAME_INDEX].text.strip(),
                    "days": extract_days(row.cells[DAYS_INDEX].text),
                    "dates": extract_dates(row.cells[DATES_INDEX].text),
                    "start_time": iso_time(row.cells[TIME_INDEX].text.split(" - ")[0]),
                    "location": row.cells[LOCATION_INDEX].text.strip()
                }
                try:
                    club["end_time"] = iso_time(row.cells[TIME_INDEX].text.split(" - ")[1])
                except IndexError:
                    club["end_time"] = ''
                clubs.append(club)

    logging.debug("Finished parsing the club spreadsheet")
    return clubs

def extract_days(days):
    days = ''.join(c for c in days if c.isalnum() or c.isspace())
    days_array = days.split()

    for i, day in enumerate(days_array):
        days_array[i] = day[0:3].capitalize()

    return days_array

def extract_dates(dates):
    """ input:
        4/8, 15, 22, 29, 5/6, 13, 20, 27, 6/3, 10, 17
        output:
        2016-04-08, 2016-04-15, 2016-04-22, 2016-04-29, ...
    """

    WORD_DOC_YEAR = WORD_DOC.tables[0].cell(0,3).text.split()[0]

    # Remove all whitespace from dates string
    dates = ''.join(dates.split())

    dates_array = dates.split(',')
    month = ''

    # Since we're modifying the array while looping, we need the index
    for i, date in enumerate(dates_array):
        date_has_month = bool('/' in date)
        if date_has_month:
            month = date[:date.index('/')]
            # Strip the date's month, for uniformity outside the if block
            date = date[date.index('/')+1:]
        try:
            dates_array[i] = datetime.date(int(WORD_DOC_YEAR), int(month), int(date)).isoformat()
        except ValueError:
            logging.exception("Invalid date in spreadsheet")
            continue

    return dates_array

def main():
    with open("clubs.json", 'w') as o:
        json.dump(parse(), o)

if __name__ == "__main__":
    main()
