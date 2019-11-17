from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Optional, Text

import requests
from bs4 import BeautifulSoup, Tag
from dynaconf import settings
from requests import Response

from benzak_etl.consts import BelorusneftCurrency, BelorusneftFuel

FUEL_CHECKBOX_ATTRS = {"name": "fuelCheckbox", "type": "checkbox"}

PRICES_TABLE_ATTRS = {"class": "beloil_table", "id": "fuel"}

PRICES_TABLE_HEADER = {"Date", "Price"}

FORM_ATTRS = {
    "action": "#",
    "id": "input",
    "method": "post",
    "name": "input",
}


def get_html(
    logger,
    *,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    currency_id: Optional[Text] = None,
    fuel_id: Optional[Text] = None,
) -> BeautifulSoup:
    logger.debug("obtaining html from belorusneft")

    kwargs = {"url": settings.BELORUSNEFT_URL}
    meth = requests.get

    if all((date_from, date_to, currency_id, fuel_id)):
        meth = requests.post
        kwargs["data"] = {
            "date1": date_from.strftime("%d.%m.%Y"),
            "date2": date_to.strftime("%d.%m.%Y"),
            "currency": currency_id,
            "fuelCheckbox": fuel_id,
        }
        logger.debug(f"form: {kwargs['data']}")

    logger.debug(f"by {meth}")

    response: Response = meth(**kwargs)

    logger.debug(f"response: {response}")

    if response.status_code != 200:
        raise RuntimeError(
            f"failed to get HTML"
            f' from the Belorusneft page "{settings.BELORUSNEFT_URL}":'
            f" status: {response.status_code},"
            f" body: {response.text},"
        )

    html = BeautifulSoup(response.text, "html.parser")

    return html


def get_form(logger, html: BeautifulSoup) -> Tag:
    logger.debug("obtaining search form")
    form = html.find("form", attrs=FORM_ATTRS)
    if not form:
        raise RuntimeError(
            f"failed to find the form"
            f" on the Belorusneft page:"
            f' "{settings.BELORUSNEFT_URL}"'
        )

    return form


def get_fuel_map(logger, form: Tag) -> Dict[Text, Text]:
    logger.debug("building fuel map")

    result = {}

    checkboxes = form.find_all("input", attrs=FUEL_CHECKBOX_ATTRS)

    for checkbox in checkboxes:
        checkbox_fuel_id = checkbox["value"]
        checkbox_fuel_name = checkbox.next.strip()

        fuel = BelorusneftFuel(checkbox_fuel_name)

        result[fuel.name] = checkbox_fuel_id

    return result


def get_currency_map(logger, form: Tag) -> Dict[Text, Text]:
    logger.debug("building currency map")

    result = {}

    options = form.find_all("option")

    for option in options:
        option_currency_name = option["value"]
        currency = BelorusneftCurrency(option_currency_name)
        result[currency.name] = option_currency_name

    return result


def get_prices(logger, html: BeautifulSoup) -> Dict[date, Decimal]:
    logger.debug("building prices table")

    table = html.find("table", attrs=PRICES_TABLE_ATTRS)
    if not table:
        raise RuntimeError(
            f"failed to find a prices table"
            f" on the Belorusneft page:"
            f' "{settings.BELORUSNEFT_URL}"'
        )

    header = ()
    parsed_rows = []

    for i, row in enumerate(table.find_all("tr")):
        if i == 0:
            header = tuple(th.text.strip() for th in row.find_all("th"))
            if set(header) != PRICES_TABLE_HEADER:
                raise RuntimeError(f"unexpected table header: {header}")
            continue

        cells = (td.text.strip() for td in row.find_all("td"))
        values = dict(zip(header, cells))
        parsed_rows.append(values)

    prices = {
        datetime.strptime(row["Date"], "%d.%m.%Y"): Decimal(row["Price"])
        for row in parsed_rows
    }

    return prices
