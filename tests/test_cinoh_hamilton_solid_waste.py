from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cinoh_hamilton_solid_waste import (
    CinohHamiltonSolidWasteSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "cinoh_hamilton_solid_waste.html"),
    url="https://www.hcdoes.org/AgendaCenter/",
)
spider = CinohHamiltonSolidWasteSpider()

freezer = freeze_time("2025-01-10")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 4


def test_title():
    assert parsed_items[0]["title"] == "Solid Waste Policy Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 11, 20, 15, 0)
    assert parsed_items[3]["start"] == datetime(2024, 2, 21, 15, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == (
        "cinoh_hamilton_solid_waste/202411201500/x/solid_waste_policy_committee"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"
    assert parsed_items[3]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Hamilton County Environmental Services",
        "address": "250 William Howard Taft Road, First Floor, Cincinnati, OH 45219",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.hcdoes.org/AgendaCenter/"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "November 20, 2024, November 20, 2024 Hamilton County Solid Waste"
            " Policy Committee Information. Media",
            "href": "https://youtu.be/7OE91Z8VOac",
        },
        {
            "title": "November 20, 2024, November 20, 2024 Hamilton County Solid Waste"
            " Policy Committee Information. Agenda",
            "href": "https://www.hcdoes.org/AgendaCenter/ViewFile/Agenda/_11202024-40",
        },
        {
            "title": "November 20, 2024, November 20, 2024 Hamilton County Solid Waste"
            " Policy Committee Information. Previous Version",
            "href": "https://www.hcdoes.org/AgendaCenter/PreviousVersions/_11202024-40",
        },
    ]
    assert parsed_items[1]["links"] == [
        {
            "title": "August 14, 2024, This is information for the August 14, 2024 "
            "Hamilton County Solid Waste Policy Committee meeting.. Minutes",
            "href": "https://www.hcdoes.org/AgendaCenter/ViewFile/Minutes/_08142024-39",
        },
        {
            "title": "August 14, 2024, This is information for the August 14, 2024 "
            "Hamilton County Solid Waste Policy Committee meeting.. Media",
            "href": "https://youtu.be/Jcx1t3pGSkI",
        },
        {
            "title": "August 14, 2024, This is information for the August 14, 2024 "
            "Hamilton County Solid Waste Policy Committee meeting.. Media",
            "href": "https://youtu.be/Jcx1t3pGSkI?si=31ayi4XHkgVdctex&t=63",
        },
        {
            "title": "August 14, 2024, This is information for the August 14, 2024 "
            "Hamilton County Solid Waste Policy Committee meeting.. Agenda",
            "href": "https://www.hcdoes.org/AgendaCenter/ViewFile/Agenda/_08142024-39",
        },
        {
            "title": "August 14, 2024, This is information for the August 14, 2024 "
            "Hamilton County Solid Waste Policy Committee meeting.. Previous Version",
            "href": "https://www.hcdoes.org/AgendaCenter/PreviousVersions/_08142024-39",
        },
    ]
    assert parsed_items[2]["links"] == [
        {
            "title": "May 15, 2024, May 15, 2024 Hamilton County Solid Waste Policy "
            "Committee Meeting Information. Minutes",
            "href": "https://www.hcdoes.org/AgendaCenter/ViewFile/Minutes/_05152024-38",
        },
        {
            "title": "May 15, 2024, May 15, 2024 Hamilton County Solid Waste Policy "
            "Committee Meeting Information. Media",
            "href": "https://youtu.be/P8zwA4pitxU",
        },
        {
            "title": "May 15, 2024, May 15, 2024 Hamilton County Solid Waste Policy "
            "Committee Meeting Information. Agenda",
            "href": "https://www.hcdoes.org/AgendaCenter/ViewFile/Agenda/_05152024-38",
        },
        {
            "title": "May 15, 2024, May 15, 2024 Hamilton County Solid Waste Policy "
            "Committee Meeting Information. Previous Version",
            "href": "https://www.hcdoes.org/AgendaCenter/PreviousVersions/_05152024-38",
        },
    ]
    assert parsed_items[3]["links"] == [
        {
            "title": "February 21, 2024, February 21, 2024 Hamilton County Solid Waste "
            "Policy Committee Meeting Information. Minutes",
            "href": "https://www.hcdoes.org/AgendaCenter/ViewFile/Minutes/_02212024-37",
        },
        {
            "title": "February 21, 2024, February 21, 2024 Hamilton County Solid Waste "
            "Policy Committee Meeting Information. Media",
            "href": "https://youtu.be/NmJIkpmUC8c",
        },
        {
            "title": "February 21, 2024, February 21, 2024 Hamilton County Solid Waste "
            "Policy Committee Meeting Information. Agenda",
            "href": "https://www.hcdoes.org/AgendaCenter/ViewFile/Agenda/_02212024-37",
        },
        {
            "title": "February 21, 2024, February 21, 2024 Hamilton County Solid Waste "
            "Policy Committee Meeting Information. Previous Version",
            "href": "https://www.hcdoes.org/AgendaCenter/PreviousVersions/_02212024-37",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
