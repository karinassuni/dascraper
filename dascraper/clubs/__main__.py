import difflib
import json
import logging
import re
from . import catalogue
from . import spreadsheet


def string_similarity(a, b):
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


def merge_clubs(spreadsheet, catalogue):
    for s in spreadsheet:
        match = {}
        for c in catalogue:
            if s["name"].lower() == c["name"].lower() \
            or string_similarity(s["name"], c["name"]) >= 0.8:
                s["description"] = c["description"]
                match = c
                break
        if match:
            catalogue.remove(match)
        else:
            logging.debug(
                "{} has no corresponding catalogue entry; description is empty"
                .format(s["name"])
            )
    return spreadsheet


def main():
    only_descriptions = catalogue.parse()
    all_but_descriptions = spreadsheet.parse()

    clubs = merge_clubs(all_but_descriptions, only_descriptions)

    with open("clubs.json", 'w') as o:
        json.dump(clubs, o, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    main()
