import datetime
import docx
import json
import logging
import os
from dascraper.clean import iso_time


# Path arguments in os.path are relative to the present working directory
# (the directory from where the module is called), so use the unchanging
# absolute path to the directory containing this file via `__file__`
WORD_DOC = docx.Document(os.path.join(os.path.dirname(
    __file__), os.path.relpath("res/ClubMeetingsSpring2016.docx")))


def parse():
    START_INDEX = 3
    NAME_INDEX, DAYS_INDEX, DATES_INDEX, TIME_INDEX, LOCATION_INDEX = range(1, 6)
    clubs = []

    logging.debug("Parsing the club spreadsheet...")

    for table in WORD_DOC.tables:
        for row in table.rows[START_INDEX:]:
            row_cells = row.cells
            club_is_active = bool(row_cells[DATES_INDEX].text.strip())
            if club_is_active:
                club = {
                    "name": row_cells[NAME_INDEX].text.strip(),
                    "days": extract_days(
                        row_cells[DAYS_INDEX].text),
                    "dates": extract_dates(
                        row_cells[DATES_INDEX].text),
                    "start_time": iso_time(
                        row_cells[TIME_INDEX].text.split(" - ")[0]),
                    "location": row_cells[LOCATION_INDEX].text.strip()
                }
                try:
                    club["end_time"] = iso_time(
                        row_cells[TIME_INDEX].text.split(" - ")[1])
                except IndexError:
                    club["end_time"] = ''
                clubs.append(club)

    logging.debug("Finished parsing the club spreadsheet")
    return clubs


def extract_days(days):
    """
    Given a string of days with arbitrary separators, return an array of ISO-
    friendly day strings
    >>> extract_days("Thursdays / Fridays")
        ["Thu", "Fri"]
    """

    # Keep spaces, for splitting the string
    clean_days = ''.join(c for c in days if c.isalpha() or c.isspace()).split()

    for i, day in enumerate(clean_days):
        clean_days[i] = day[0:3].capitalize()

    return clean_days


def extract_dates(dates):
    """
    Given a string of dates with arbitrary separators, return an array of ISO dates
    >>> extract_dates("4/8, 15, 22, 29")
        ["2016-04-08", "2016-04-15", "2016-04-22", "2016-04-29"]
    """

    WORD_DOC_YEAR = int(WORD_DOC.tables[0].cell(0, 3).text.split()[0])

    # Remove all whitespace from dates string
    clean_dates = ''.join(dates.split()).split(',')

    month = 0

    # Since we're modifying the array while looping, we need the index
    for i, date in enumerate(clean_dates):
        date_has_month = bool('/' in date)
        if date_has_month:
            month = int(date[:date.index('/')])
            # Strip the date's month, for uniformity outside the if block
            date = date[date.index('/') + 1:]
        try:
            clean_dates[i] = datetime.date(
                WORD_DOC_YEAR, month, int(date)).isoformat()
        except ValueError:
            logging.exception("Invalid date in spreadsheet")
            continue

    return clean_dates


def main():
    with open("clubs.json", 'w') as o:
        json.dump(parse(), o)


if __name__ == "__main__":
    main()
