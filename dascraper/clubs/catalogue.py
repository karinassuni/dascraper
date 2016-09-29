import dascraper.utility.requests as requests
import json
from lxml import etree


def parse():
    r = requests.attempt("GET", "https://www.deanza.edu/clubs/clublist_name.html")

    root = etree.HTML(r.content)

    club_names = root.xpath(
        '//h6[not(a)]/text()'
    )
    club_descriptions = clean_descriptions(
        root.xpath(
            '//h6[not(a)]/following-sibling::node()[position() = 3]'
        )
    )

    return {
        n: {"description": d}
        for n, d
        in zip(club_names, club_descriptions)
    }


def clean_descriptions(descriptions):
    return [description.replace('\r\n', '\n') for description in descriptions]


def main():
    with open("clubs_with_only_descriptions.json", 'w') as o:
        json.dump(parse(), o, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    main()
