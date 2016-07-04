# TODO: generate EVENTS from club data
# TODO: for EVENTS in here and the calendar parser, create two fields start_time and end_time to replace time, whose values are UNIX timestamps
# TODO: reformat the "dates" fields of CLUBS to be an array of some universal string date representation
import docx
import datetime
import json

WORD_DOC = docx.Document("ClubMeetingsSpring2016.docx")

def main():
    START_INDEX = 3
    NAME_INDEX, DAYS_INDEX, DATES_INDEX, TIME_INDEX, LOCATION_INDEX = range(1, 6)
    clubs = []
    print "Parsing the club spreadsheet..."
    for table in WORD_DOC.tables:
        for row in table.rows[START_INDEX:]:
            club_is_active = bool(row.cells[DATES_INDEX].text.strip())
            if club_is_active:
                club = {
                    "name": row.cells[NAME_INDEX].text.strip(),
                    "days": clean_days(row.cells[DAYS_INDEX].text).split(),
                    "dates": clean_dates(row.cells[DATES_INDEX].text).split(", "),
                    "start_time": clean_time(row.cells[TIME_INDEX].text.split(" - ")[0]),
                    "location": row.cells[LOCATION_INDEX].text.strip()
                }
                try:
                    club["end_time"] = clean_time(row.cells[TIME_INDEX].text.split(" - ")[1])
                except IndexError:
                    club["end_time"] = ''
                clubs.append(club)
    with open("clubs.json", 'w') as outfile:
        json.dump(clubs, outfile)
    print "Finished!"

def clean_days(days):
    # Keep only alphanumeric characters, and whitespace for splitting the string into list items
    days_array = ''.join(char for char in days if char.isalnum() or char.isspace()).split()
    for i, day in enumerate(days_array):
        days_array[i] = days_array[i][0:2].capitalize()

    return ' '.join(days_array).strip()

def clean_dates(dates):
    """ input:
        4/8, 15, 22, 29, 5/6, 13, 20, 27, 6/3, 10, 17
        output:
        4/8/16, 4/15/16, 4/22/16, 4/29/16
    """

    month = ''
    WORD_DOC_YEAR = WORD_DOC.tables[0].cell(0,3).text.split()[0]
    dates_array = dates.split(", ")
    # Since we need to modify each list element as we loop, we need to access indicies
    for i, date in enumerate(dates_array):
        date_has_month = bool('/' in date)
        if date_has_month:
            month = date[:date.index('/')]
        else:
            dates_array[i] = month + '/' + dates_array[i]
        dates_array[i] = dates_array[i] + '/' + WORD_DOC_YEAR

    return ", ".join(dates_array).strip()

def clean_time(time):
    time = time.lower()
    if 'a' in time:
        time = time.split()[0] + 'a'
    elif 'p' in time:
        time = time.split()[0] + 'p'
    return time

if __name__ == "__main__":
    main()

