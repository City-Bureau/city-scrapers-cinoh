from urllib.parse import urljoin

from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class CinohHamiltonSolidWasteSpider(CityScrapersSpider):
    name = "cinoh_hamilton_solid_waste"
    agency = "Hamilton County Solid Waste Policy Committee"
    timezone = "America/New_York"
    start_urls = ["https://www.hcdoes.org/AgendaCenter/"]
    location = {
        "name": "Hamilton County Environmental Services",
        "address": "250 William Howard Taft Road, First Floor, Cincinnati, OH 45219",
    }

    def parse(self, response):
        """
        Parse data from meetings table.
        """
        for item in response.css("tbody tr"):
            meeting = Meeting(
                title="Solid Waste Policy Committee",
                description="",
                classification=COMMITTEE,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item):
        """
        Parse start datetime as a naive datetime object.
        All the meetings in the agendas started at 3pm. Continue using 3pm.
        """
        text = item.css("strong::attr(aria-label)").get()
        if " for " in text:
            date = text.split(" for ")[1]
            return parse(f"{date} 3pm")
        else:
            return None

    def _parse_links(self, item):
        """Parse or generate links."""
        base_url = "https://www.hcdoes.org/"
        output = []
        links = item.css(".minutes a, .media a, .popout a")
        for link in links:
            title = link.css("::attr(aria-label)").get()
            href = link.css("::attr(href)").get()
            url = urljoin(base_url, href)
            output.append({"title": title, "href": url})

        return output

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
