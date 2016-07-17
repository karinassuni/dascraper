import difflib
import json
import logging
import re
from . import catalogue
from . import spreadsheet


def filter_words(club_name):
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


def similarity(str1, str2):
    return difflib.SequenceMatcher(
        a=filter_words(str1), b=filter_words(str2)
    ).ratio()


def main():
    clubs_with_only_descriptions = catalogue.parse()
    clubs_without_descriptions = spreadsheet.parse()

    for c in clubs_without_descriptions:
        best_similarity = 0.68
        matched_d = {}
        for d in clubs_with_only_descriptions:
            if c["name"].lower() == d["name"].lower() \
            or similarity(c["name"], d["name"]) >= 0.8:
                c["description"] = d["description"]
                matched_d = d
                break
            elif similarity(c["name"], d["name"]) >= best_similarity:
                c["description"] = d["description"]
                matched_d = d
                best_similarity = similarity(c["name"], d["name"])
                logging.info("{0} || {1} : {2}".format(
                    filter_words(c["name"]),
                    filter_words(d["name"]),
                    similarity(c["name"], d["name"])
                ))
        if matched_d:
            clubs_with_only_descriptions.remove(matched_d)
        else:
            logging.debug(
                "{} has no corresponding catlaogue entry w/ description"
                .format(c["name"])
            )

    with open("clubs.json", 'w') as o:
        json.dump(clubs_without_descriptions, o, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    main()
