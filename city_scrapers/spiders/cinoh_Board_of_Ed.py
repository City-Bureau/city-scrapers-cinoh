from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD, COMMISSION, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


class CinohBoardOfEdSpider(CityScrapersSpider):
    name = "cinoh_Board_of_Ed"
    agency = "Cincinnati Board of Education"
    timezone = "America/New_York"
    committee_id = "A9HCZC3376F4"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    # the original URL is https://go.boarddocs.com/oh/cps/Board.nsf/Public#tab-welcome
    # the html is not scrapable but clicking on the meetings will bring up two
    # API endpoints containing the data for the meeting list. I was only able to
    # scrape one of these endpoints which is the one below.
    # the current API scraping method is based on another previous scaper for
    # the boarddocs website: https://github.com/City-Bureau/city-scrapers-cinoh/pull/10

    def start_requests(self):
        url = "https://go.boarddocs.com/oh/cps/Board.nsf/BD-GetMeetingsList"
        form_data = {"current_committee_id": self.committee_id}
        yield scrapy.FormRequest(url, formdata=form_data, callback=self.parse)

    def parse(self, response):
        lower_limit = datetime.now() - relativedelta(months=12)
        data = response.json()
        # hardcoded location
        location = {
            "name": "Cincinnati Public Schools",
            "address": "2651 Burnet Avenue, Mary A. Ronan Education Center "
            "Room 111, Cincinnati, OH 45219",
        }

        meeting_source = "https://go.boarddocs.com/oh/cps/Board.nsf/Public#"

        for item in data:

            date = item.get("numberdate")
            if date is None:
                continue
            meeting_date = parse(date)
            if meeting_date < lower_limit:
                continue

            meeting = Meeting(
                title=item["name"],
                description="",
                classification=self._parse_classification(item),
                start=parse(date),
                end=None,
                all_day=False,
                time_notes="",
                location=location,
                links=self._parse_links(item),
                source=meeting_source,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_classification(self, item):
        if "Committee" in item["name"]:
            return COMMITTEE
        elif "Board" in item["name"]:
            return BOARD
        elif "Commission" in item["name"]:
            return COMMISSION
        else:
            return NOT_CLASSIFIED

    def _parse_links(self, item):
        # each link is to the full meeting agenda and
        # also contains the meeting's Zoom link
        """Generate links."""
        href = (
            f"https://go.boarddocs.com/oh/cps/Board.nsf/Download-AgendaDetailed?"
            f"open&id={item['unique']}&current_committee_id={self.committee_id}"
        )
        return [{"title": "Agenda and Zoom Meeting Link", "href": href}]
