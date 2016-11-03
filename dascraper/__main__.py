import dascraper.eventscalendar.calendar as calendar
import dascraper.clubs.__main__ as clubs
import pyrebase


def main():
    events = calendar.main()
    organizations = clubs.main()

    config = {
        "apiKey": "AIzaSyA9W2k7hzFFVUt3y82KTdQbetcSdUAYn6M",
        "authDomain": "de-anza-calendar.firebaseapp.com",
        "databaseURL": "https://de-anza-calendar.firebaseio.com",
        "storageBucket": "de-anza-calendar.appspot.com",
        "serviceAccount": "De Anza Calendar-67c1fd8e425d.json"
    }

    db = pyrebase.initialize_app(config).database()
    eventsRef = db.child("events")
    organizationsRef = db.child("organizations")

    eventsRef.update(events)
    organizationsRef.update(organizations)


if __name__ == "__main__":
    main()
