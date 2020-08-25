import re
from collections import defaultdict
from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ClayPlanArbSpider(CityScrapersSpider):
    name = "clay_plan_arb"
    agency = "Clayton Plan Commission and Architectural Review Board"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.claytonmo.gov/government/boards-and-commissions/plan-commission-and-architectural-review-board"
    ]
    
    def __init__(self, *args, **kwargs):
        self.agenda_map = defaultdict(list)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        yield from self._parse_meetings_page(response)

    def _parse_meetings_page(self, response):
        url = "https://www.claytonmo.gov/calendar/meetings/-seldept-8/-toggle-all"
        yield scrapy.Request(url=url, callback=self._parse_calendar_page)

    def _parse_calendar_page(self, response):
        for item in self._get_event_urls(response):
            yield scrapy.Request(url=item, callback=self._parse_event, dont_filter=True)

    def _get_event_urls(self, response):
        descriptions = response.css("h2.vi-events-tiles-title::text").getall()
        links = response.css("li.vi-events-tiles-item a::attr(href)").getall()

        urls = []

        for description, link in zip(descriptions, links):
            if "plan commission/arb" in description.lower() or "ARB" in description:
                url = response.urljoin(link)

                pattern = r"(?P<link>.*/\d{4})"
                rm = re.search(pattern, url)

                if rm is not None:
                    urls.append(rm.group("link"))

        return urls

    def _parse_event(self, response):
        start = self._parse_start(response)
        meeting = Meeting(
            title=self._parse_title(response),
            description="",
            classification=BOARD,
            start=start,
            end=self._parse_end(response),
            all_day=False,
            time_notes="",
            location=self._parse_location(response),
            links=self._parse_links(response, start),
            source=response.url,
        )
        # meeting["status"] = self._get_status(meeting)
        # meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        return response.css('h2.detail-title span::text')

    def _parse_start(self, response):
        """Parse start datetime as a naive datetime object."""
        date = response.css("span.detail-list-value::text").get()
        pattern = r"(?P<day>\d{2}/\d{2}/\d{4}) (?P<time>\d{1,2}:\d{2} (PM|AM)) - "
        pattern += r"\d{1,2}:\d{2} (PM|AM)"

        rm = re.search(pattern, str(date))

        if rm is not None:
            day = rm.group("day")
            time = rm.group("time")
            dt = day + " " + time
            start = datetime.strptime(dt.strip(), "%m/%d/%Y %H:%M %p")
            return start
        else:
            return None

    def _parse_end(self, response):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        end = response.css("span[itemprop='endDate']::text").get()
        pattern = r"(?P<day>\d{2}/\d{2}/\d{4}), (?P<time>(\d{1,2}:\d{2}) (PM|AM))"
        pattern += r" - (\d{1,2}:\d{2}) (PM|AM)"

        rm = re.search(pattern, str(end))

        if rm is not None:
            day = rm.group("day")
            time = rm.group("time")
            dt = day + " " + time
            start = datetime.strptime(dt.strip(), "%m/%d/%Y %H:%M %p")
            return start
        else:
            return None

    def _parse_location(self, response):
        """Parse or generate location."""
        return {
            "address": response.css(
                "span[itemprop='location'] span[itemprop='street-address']::text"
            ).get(),
            "name": response.css(
                "span[itemprop='location'] span[itemprop='name']::text"
            ).get(),
        }

    def _parse_links(self, response, date):
        """Parse or generate links for additional material, i.e. agendas."""
        url = "https://www.claytonmo.gov/government/boards-and-commissions/plan-commission-and-architectural-review-board"
        yield scrapy.Request(url=url, callback=self._pair_agenda_to_event(date))

    def pair_agenda_to_event(self, date):
        pattern = r"(?P<day>\d{2}/\d{2}/\d{2}), (?P<time>(\d{1,2}:\d{2}) (PM|AM))"
        pattern += r" - (\d{1,2}:\d{2}) (PM|AM)"
        rm = re.search(pattern, date)
        if rm is not None:
            agenda = response.css("span.detail-list-value a::attr(href)").get()
            return agenda
        return None
