import re
from datetime import datetime
from urllib.parse import unquote, urljoin
from zoneinfo import ZoneInfo

import scrapy
from city_scrapers_core.constants import BOARD, COMMISSION, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dt_parser
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrulestr
from scrapy import Selector


class CinohHamiltonCountyMixinMeta(type):
    """
    Metaclass that enforces the implementation of required static
    variables in child classes that inherit from the "Mixin" class.
    """

    def __init__(cls, name, bases, dct):
        required_static_vars = [
            "agency",
            "name",
            "categories",
        ]
        missing_vars = [var for var in required_static_vars if var not in dct]

        if missing_vars:
            missing_vars_str = ", ".join(missing_vars)
            raise NotImplementedError(
                f"{name} must define the following static variable(s): "
                f"{missing_vars_str}."
            )

        super().__init__(name, bases, dct)


class CinohHamiltonCountyMixin(
    CityScrapersSpider, metaclass=CinohHamiltonCountyMixinMeta
):
    name = None
    agency = None
    categories = None
    timezone = "America/New_York"
    tz = ZoneInfo(timezone)

    base_url = "https://www.hamiltoncountyohio.gov/"
    source_url = "https://www.hamiltoncountyohio.gov/calendar.php"
    primary_api = "https://www.hamiltoncountyohio.gov/_assets_/plugins/revizeCalendar/calendar_data_handler.php?webspace=hamiltoncountyoh&relative_revize_url=//cms2.revize.com&protocol=https:"  # noqa

    attachments_base_url = "https://hcjfsonbase.jfs.hamilton-co.org"
    attachments_url = "https://hcjfsonbase.jfs.hamilton-co.org/OnBaseAgendaOnline"

    ADDRESS_SPLIT_PATTERN = re.compile(r"\b\d+[A-Za-z]?\s+(?=[NSEW]?\.?\s?[A-Za-z])")
    CANCELLED_PATTERN = re.compile(r"\(cancel{1,2}ed\)", re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = datetime.now(tz=self.tz).replace(tzinfo=None)
        self.window_start = now - relativedelta(years=1)
        self.window_end = now + relativedelta(years=1)
        self._seen_dates = set()

    def start_requests(self):
        yield scrapy.Request(
            url=self.attachments_url,
            callback=self._parse_bocc_attachments,
        )

    def _parse_bocc_attachments(self, response):
        attachment_records = self._bocc_attachments(response)

        yield scrapy.Request(
            url=self.primary_api,
            callback=self.parse,
            cb_kwargs={"attachment_records": attachment_records},
        )

    def _bocc_attachments(self, response):
        attachments = {}
        for row in response.css(".meeting-row"):
            title = row.css('td[data-sortable-type="mtgName"]::text').get()
            dt_text = row.css('td[data-sortable-type="mtgTime"]::text').get()
            if not (title and dt_text):
                continue

            dt_object = dt_parser(dt_text)
            dt_string = dt_object.strftime("%Y-%m-%d %H:%M:%S")

            url_second_half = row.css("a::attr(href)").get()
            link = urljoin(self.attachments_base_url, url_second_half)
            attachments[dt_string] = link
        return attachments

    def parse(self, response, attachment_records):
        records = self._handle_rrule(response)
        for record in records:
            meeting_key = (record.get("title"), record.get("start"))
            if meeting_key not in self._seen_dates:
                self._seen_dates.add(meeting_key)
                if record.get("primary_calendar_name") in self.categories:
                    raw_title = record.get("title") or ""
                    meeting = Meeting(
                        title=self._parse_title(raw_title),
                        description=self._parse_description(record),
                        classification=self._parse_classification(raw_title),
                        start=self._parse_start(record),
                        end=self._parse_end(record),
                        all_day=record.get("allDay") or False,
                        time_notes="",
                        location=self._parse_location(record),
                        links=self._parse_links(record, attachment_records),
                        source=self._parse_source(record),
                    )

                    meeting["status"] = self._get_status(meeting, text=raw_title)
                    meeting["id"] = self._get_id(meeting)

                    yield meeting

    def _handle_rrule(self, response):
        """
        The meeting-listing used in this scraper API doesn't provide every
        occurrence of a recurring meeting. Instead, it returns a recurrence
        rule ('rrule') describing the cadence. This method expands each rrule
        into actual meeting dates, bounded by the spider's date window, and
        passes non-recurring meetings through unchanged.
        """
        records = []
        for record in response.json():
            start_dt = record.get("start")
            end_dt = record.get("end")

            if not record.get("rrule"):
                records.append(record)
                continue

            rset = rrulestr(record.get("rrule"), forceset=True)

            if start_dt and end_dt:
                duration = datetime.fromisoformat(end_dt) - datetime.fromisoformat(
                    start_dt
                )
            else:
                duration = None

            for occurence in rset.between(self.window_start, self.window_end, inc=True):
                r_event = record.copy()
                r_event["start"] = occurence.isoformat()
                r_event["end"] = (
                    (occurence + duration).isoformat() if duration else None
                )
                r_event.pop("rrule", None)
                records.append(r_event)

        return records

    def _parse_title(self, raw_title):
        return self.CANCELLED_PATTERN.sub("", raw_title).strip()

    def _parse_description(self, record):
        desc_html = unquote(record.get("desc") or "")
        desc_html = re.sub(r"(?i)</p\s*>|<br\s*/?>", "\n", desc_html)

        desc_selector = Selector(text=desc_html)

        for anchor in desc_selector.xpath("//a"):
            raw_href = (anchor.xpath("@href").get() or "").strip()
            href = self._href_classify(raw_href)
            label = (anchor.xpath("string(.)").get() or "").strip()

            el = anchor.root
            el.text = f"{label} ({href})" if href else label
            for child in list(el):
                el.remove(child)

        desc_text = desc_selector.xpath("string(/)").get()
        desc_cleaned = re.sub(r"\n{2,}", "\n", desc_text).strip()
        return desc_cleaned

    def _href_classify(self, href):
        if not href.startswith("http"):
            return urljoin(self.base_url, href)
        return href

    def _parse_classification(self, title):
        classification_keywords = [
            (
                BOARD,
                (
                    "commissioner",
                    "bocc",
                    "board",
                ),
            ),
            (COMMISSION, ("commission",)),
        ]
        for classification, keywords in classification_keywords:
            if any(keyword in title.lower() for keyword in keywords):
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, record):
        start_dt = record.get("start")
        if start_dt:
            return datetime.fromisoformat(start_dt)
        else:
            self.logger.warning(f"Failed to parse meeting start time: {start_dt}")
            return None

    def _parse_end(self, record):
        end_dt = record.get("end")
        return datetime.fromisoformat(end_dt) if end_dt else None

    def _parse_location(self, record):
        location = {
            "name": "",
            "address": "",
        }
        raw_address = (record.get("location") or "").strip()
        if not raw_address:
            return location

        match = self.ADDRESS_SPLIT_PATTERN.search(raw_address)
        if not match:
            location["name"] = raw_address
            return location

        name = raw_address[: match.start()].strip(" ,")
        address = raw_address[match.start() :].strip(" ,")

        return {
            "name": name,
            "address": address,
        }

    def _parse_links(self, record, attachment_records):
        desc_text = unquote(record.get("desc") or "")
        if "hcjfsonbase.jfs.hamilton-co.org" in desc_text:
            start_dt_str = datetime.fromisoformat(record.get("start")).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            matched_link = attachment_records.get(start_dt_str)
            if matched_link:
                return [
                    {
                        "title": "Agenda, Notes, and Media",
                        "href": matched_link,
                    }
                ]
        elif "business_detail_T" in desc_text:
            detail_url = self._extract_detail_url(record)
            return [
                {
                    "title": "Attachments Page",
                    "href": detail_url,
                }
            ]
        return []

    def _extract_detail_url(self, record):
        desc_html = unquote(record.get("desc") or "")
        desc_selector = Selector(text=desc_html)

        for anchor in desc_selector.xpath("//a"):
            raw_href = (anchor.xpath("@href").get() or "").strip()
            href = self._href_classify(raw_href)
            if "business_detail_T" in href:
                return href
        return None

    def _parse_source(self, record):
        event_id = record.get("id")
        if event_id:
            return f"{self.source_url}?event={event_id}"
        return self.source_url
