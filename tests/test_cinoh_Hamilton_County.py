from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cinoh_Hamilton_County import (
    CinohHamiltonBoardsCommissionsSpider,
    CinohHamiltonCommissionSpider,
)

attachments_response = file_response(
    join(dirname(__file__), "files", "cinoh_Hamilton_Commission.html"),
    url="https://hcjfsonbase.jfs.hamilton-co.org/OnBaseAgendaOnline",
)

meetings_response = file_response(
    join(dirname(__file__), "files", "cinoh_Hamilton_Commission_api.json"),
    url="https://www.hamiltoncountyohio.gov/_assets_/plugins/revizeCalendar/calendar_data_handler.php?webspace=hamiltoncountyoh&relative_revize_url=//cms2.revize.com&protocol=https",  # noqa
)


@pytest.fixture
def commission_items():
    with freeze_time("2026-08-17"):
        spider = CinohHamiltonCommissionSpider()
        attachments = spider._bocc_attachments(attachments_response)
        return [item for item in spider.parse(meetings_response, attachments)]


@pytest.fixture
def boards_items():
    with freeze_time("2026-08-17"):
        spider = CinohHamiltonBoardsCommissionsSpider()
        attachments = spider._bocc_attachments(attachments_response)
        return list(spider.parse(meetings_response, attachments))


def test_count(commission_items, boards_items):
    assert len(commission_items) == 166
    assert len(boards_items) == 116


def test_title(commission_items, boards_items):
    assert commission_items[0]["title"] == "Commissioner Meeting"
    assert boards_items[0]["title"] == "Board of Building Appeals"


def test_description(commission_items, boards_items):
    assert commission_items[0]["description"] == "\n".join(
        [
            "Address - Todd B. Portune Center of County Government,",
            "138 East Court St. 6th Floor, Cincinnati, OH 45202",
            "Agenda & Minutes (https://hcjfsonbase.jfs.hamilton-co.org/OnBaseAgendaOnline)",  # noqa
        ]
    )
    assert boards_items[0]["description"] == ""


def test_start(commission_items, boards_items):
    assert commission_items[0]["start"] == datetime(2025, 8, 28, 10, 0)
    assert boards_items[0]["start"] == datetime(2025, 9, 3, 9, 15)


def test_end(commission_items, boards_items):
    assert commission_items[0]["end"] == datetime(2025, 8, 28, 11, 30)
    assert boards_items[0]["end"] == datetime(2025, 9, 3, 11, 30)


def test_time_notes(commission_items, boards_items):
    assert commission_items[0]["time_notes"] == ""
    assert boards_items[0]["time_notes"] == ""


def test_id(commission_items, boards_items):
    assert (
        commission_items[0]["id"]
        == "cinoh_hamilton_commission/202508281000/x/commissioner_meeting"
    )
    assert (
        boards_items[0]["id"]
        == "cinoh_hamilton_boards_commissions/202509030915/x/board_of_building_appeals"
    )


def test_status(commission_items, boards_items):
    assert commission_items[0]["status"] == "passed"
    assert boards_items[0]["status"] == "passed"


def test_location(commission_items, boards_items):
    assert commission_items[0]["location"] == {
        "name": "Todd B. Portune Center of County Government",
        "address": "138 East Court St. 6th Floor, Cincinnati, OH 45202",
    }
    assert boards_items[0]["location"] == {
        "name": "Todd B. Portune Center of County Government",
        "address": "138 East Court St. Room 805, Cincinnati, OH 45202",
    }


def test_source(commission_items, boards_items):
    assert (
        commission_items[0]["source"]
        == "https://www.hamiltoncountyohio.gov/calendar.php?event=14"
    )
    assert (
        boards_items[0]["source"]
        == "https://www.hamiltoncountyohio.gov/calendar.php?event=52"
    )


def test_links(commission_items, boards_items):
    assert commission_items[0]["links"] == [
        {
            "href": "https://hcjfsonbase.jfs.hamilton-co.org/OnBaseAgendaOnline/Meetings/ViewMeeting?id=2800&doctype=1",  # noqa
            "title": "Agenda, Notes, and Media",
        }
    ]
    assert boards_items[0]["links"] == []


def test_classification(commission_items, boards_items):
    assert commission_items[0]["classification"] == BOARD
    assert boards_items[0]["classification"] == BOARD
