import dascraper.eventcalendar.calendar as calendar
import dascraper.clubs.spreadsheet as spreadsheet
import logging
import os


def main():
    logging.basicConfig(
        filename=os.path.join(
            os.environ.get("OPENSHIFT_DATA_DIR"), "logs/", "dascraper.py.log"),
        level=logging.DEBUG,
        format="%(levelname)8s: %(asctime)s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p"
    )
    logging.info("********** NEW PARSE **********")
    calendar.main()
    spreadsheet.main()
    logging.info("********** DONE PARSE **********")


if __name__ == "__main__":
    main()
