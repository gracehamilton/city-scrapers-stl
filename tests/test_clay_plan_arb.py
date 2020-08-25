from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.clay_plan_arb import ClayPlanArbSpider

test_response = file_response(
    join(dirname(__file__), "files", "clay_plan_arb.html"),
    url="https://www.claytonmo.gov/Home/Components/Calendar/Event/4588/1502?seldept=8&toggle=all",
)
spider = ClayPlanArbSpider()

freezer = freeze_time("2020-08-19")
freezer.start()

parsed_items = [item for item in spider._parse_event(test_response)]

freezer.stop()



"""
Uncomment below
"""

def test_title():
    assert parsed_items[0]["title"] == "Planning Commission/Architectural Review Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 12, 21, 5, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2020, 12, 21)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


# def test_id():
#     assert parsed_items[0]["id"] == "EXPECTED ID"


# def test_status():
#     assert parsed_items[0]["status"] == "EXPECTED STATUS"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Hall",
        "address": "10 N. Bemiston Ave Clayton, Missouri 63105"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.claytonmo.gov/Home/Components/Calendar/Event/4588/1502?seldept=8&toggle=all"


# def test_links():
#     assert parsed_items[0]["links"] == [{
#       "href": "EXPECTED HREF",
#       "title": "EXPECTED TITLE"
#     }]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_all_day():
    assert parsed_items[0]["all_day"] is False
