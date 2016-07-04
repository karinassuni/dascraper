from docx import Document
import json

WORD_DOC = Document("ClubMeetingsSpring2016.docx")

def main():
    NAME_INDEX, DAYS_INDEX, DATES_INDEX, TIME_INDEX, LOCATION_INDEX = range(1, 6)
    clubs = []
    print "Parsing the club spreadsheet..."
    for table in WORD_DOC.tables:
        for row in table.rows[3:]:
            club_is_active = bool(row.cells[DATES_INDEX].text.strip())
            if club_is_active:
                clubs.append({
                    "name": row.cells[NAME_INDEX].text,
                    "days": row.cells[DAYS_INDEX].text,
                    "dates": row.cells[DATES_INDEX].text,
                    "time": row.cells[TIME_INDEX].text,
                    "location": row.cells[LOCATION_INDEX].text
                })
    with open("clubs.json", 'w') as outfile:
        json.dump(clubs, outfile)
    print "Finished!"

if __name__ == "__main__":
    main()

