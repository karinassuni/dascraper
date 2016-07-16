import requests
from lxml import etree

def parse():
    r = requests.get("https://www.deanza.edu/clubs/clublist_name.html")
    root = etree.HTML(r.content)
    club_names = root.xpath(
        '//h6[not(a)]/text()'
    )
    club_descriptions = root.xpath(
        '//h6[not(a)]/following-sibling::node()[position() = 3]'
    )
    return [
        {"name": n, "description": d}
        for n, d
        in zip(club_names, club_descriptions)
    ]
