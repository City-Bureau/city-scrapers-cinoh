from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cinoh_Board_of_Ed import CinohBoardOfEdSpider

test_response = file_response(
    join(dirname(__file__), "files", "cinoh_Board_of_Ed.json"),
    url="https://go.boarddocs.com/oh/cps/Board.nsf/BD-GetMeetingsList",
)
spider = CinohBoardOfEdSpider()

freezer = freeze_time("2024-12-30")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Budget, Finance and Growth Committee Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 12, 20, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "cinoh_Board_of_Ed/202412200000/x/budget_finance_and"
        "_growth_committee_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Cincinnati Public Schools",
        "address": "2651 Burnet Avenue, Mary A. Ronan Education Center "
        "Room 111, Cincinnati, OH 45219",
    }


def test_source():
    assert (
        parsed_items[0]["source"] == "https://go.boarddocs.com/oh/cps/Board.nsf/Public#"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://go.boarddocs.com/oh/cps/Board.nsf/Download-AgendaDetailed?"
            "open&id=DC2QWY6B5DDA&current_committee_id=A9HCZC3376F4",
            "title": "Agenda and Zoom Meeting Link",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
