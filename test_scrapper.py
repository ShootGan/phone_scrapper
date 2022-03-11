"""Scraper pytest file"""


import main
import bs4


def test_type():
    assert main.get_phone_number("https://zsbrybnik.pl/") == '+32 42 222 79'
