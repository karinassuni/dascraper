import difflib
import json
import logging
import re
import requests
from . import catalogue
from . import spreadsheet


def name_similarity(a, b):
    return difflib.SequenceMatcher(
        a=filter_name(a), b=filter_name(b)
    ).ratio()


def filter_name(club_name):
    common_substrings = [
        "De Anza College",
        "De Anza",
        "DA",
        "Student",
        "Scholar",
        "Association",
        "Club",
        "and",
        "of",
        "at",
        "the"
    ]

    for s in common_substrings:
        # Remove common_substrings and their plurals
        club_name = re.sub(s + 's?', '', club_name)

    # Remove club initialism
    club_name = re.sub('\(.*\)$', '', club_name)

    # Normalize spaces
    club_name = re.sub(' +', ' ', club_name).strip()

    return club_name


def absorb_descriptions(source, target):
    for t_key, t_dict in target.items():
        for s_key, s_dict in source.items():
            if t_key.lower() == s_key.lower() \
            or name_similarity(t_key, s_key) >= 0.8:
                t_dict.update(s_dict)
                del source[s_key]
                break
        else:
            logging.debug(
                "{} has no corresponding source entry; description nulled"
                .format(t_key)
            )
    return target


def main():
    catalogue_clubs = catalogue.parse()
    spreadsheet_clubs = spreadsheet.parse()

    clubs = absorb_descriptions(catalogue_clubs, spreadsheet_clubs)

    headers = {'content-type': 'application/json'}
    requests.patch("https://de-anza-calendar.firebaseio.com/organizations", data=clubs, headers=headers)

    with open("clubs.json", 'w') as o:
        json.dump(clubs, o, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    main()
