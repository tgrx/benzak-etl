import logging
from datetime import datetime
from decimal import Decimal

from bs4 import BeautifulSoup

from benzak_etl.providers.belorusneft import transform_prices


def test(caplog, belorusneft_prices_page):
    caplog.set_level(logging.CRITICAL)
    logger = logging.getLogger()

    expected = {
        "10.05.2020": "1.78",
        "03.05.2020": "1.79",
        "26.04.2020": "1.8",
        "19.04.2020": "1.81",
        "12.04.2020": "1.82",
        "01.03.2020": "1.83",
        "23.02.2020": "1.82",
        "16.02.2020": "1.81",
        "09.02.2020": "1.8",
        "02.02.2020": "1.79",
        "26.01.2020": "1.78",
        "19.01.2020": "1.77",
        "12.01.2020": "1.76",
        "05.01.2020": "1.75",
        "29.12.2019": "1.74",
        "22.12.2019": "1.73",
        "15.12.2019": "1.72",
        "08.12.2019": "1.71",
        "01.12.2019": "1.7",
        "24.11.2019": "1.69",
        "29.09.2019": "1.68",
        "22.09.2019": "1.67",
        "15.09.2019": "1.66",
        "11.08.2019": "1.65",
        "21.07.2019": "1.66",
        "16.06.2019": "1.67",
        "09.06.2019": "1.68",
        "02.06.2019": "1.69",
        "26.05.2019": "1.68",
        "19.05.2019": "1.67",
        "13.05.2019": "1.66",
    }

    expected = {
        datetime.strptime(_d, "%d.%m.%Y"): Decimal(_p) for _d, _p in expected.items()
    }

    soup = BeautifulSoup(belorusneft_prices_page, features="html.parser")
    got = transform_prices(logger, soup)
    assert expected == got
