import json
from datetime import date
from datetime import datetime
from decimal import Decimal
from typing import Dict
from typing import Optional
from typing import Text

from aiohttp import ClientResponse
from bs4 import BeautifulSoup
from bs4 import Tag
from dynaconf import settings

from benzak_etl.consts import BelorusneftCurrency
from benzak_etl.consts import BelorusneftFuel

_FUEL_CHECKBOX_ATTRS = {"name": "fuelCheckbox", "type": "checkbox"}
_FUEL_CHECKBOX_HTML = (
    "<input "
    + " ".join(f'{_a}="{_v}"' for _a, _v in sorted(_FUEL_CHECKBOX_ATTRS.items()))
    + ">"
)

_PRICES_TABLE_ATTRS = {"class": "beloil_table"}
_PRICES_TABLE_HTML = (
    "<table "
    + " ".join(f'{_a}="{_v}"' for _a, _v in sorted(_PRICES_TABLE_ATTRS.items()))
    + ">"
)

_PRICES_TABLE_HEADER = {"Date", "Price"}

_FORM_ATTRS = {
    "action": "#",
    "id": "input",
    "method": "post",
    "name": "input",
}
_FORM_HTML = (
    "<form " + " ".join(f'{_a}="{_v}"' for _a, _v in sorted(_FORM_ATTRS.items())) + ">"
)


async def extract_html(
    logger,
    session,
    *,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    currency_id: Optional[Text] = None,
    fuel_id: Optional[Text] = None,
) -> BeautifulSoup:
    logger.debug(f'using Belorusneft URL: "{settings.BELORUSNEFT_URL}"')

    kwargs = {"url": settings.BELORUSNEFT_URL}
    meth = session.get

    # TODO: all->any, but skip empty in kwargs
    if all((date_from, date_to, currency_id, fuel_id)):
        meth = session.post
        kwargs["data"] = {
            "date1": date_from.strftime("%d.%m.%Y"),
            "date2": date_to.strftime("%d.%m.%Y"),
            "currency": currency_id,
            "fuelCheckbox": fuel_id,
        }
        logger.debug(
            f"using form data:"
            f" {json.dumps(kwargs['data'], indent=2, sort_keys=True)}"
        )

    logger.debug(f"sending request with method: {meth.__name__}")

    response: ClientResponse = await meth(**kwargs)
    logger.debug(f"got response: {response.status} {response.reason}")

    text = await response.text()

    if response.status != 200:
        raise RuntimeError(
            f"failed to get HTML"
            f' from the Belorusneft page "{settings.BELORUSNEFT_URL}":'
            f" status: {response.status},"
            f" body: {text},"
        )

    logger.debug(f"transforming body into html")

    html = BeautifulSoup(text, "html.parser")
    logger.debug(f"transformed html: {len(html)} tags")

    return html


def extract_form(logger, html: BeautifulSoup) -> Tag:
    logger.debug(f"looking for {_FORM_HTML}")

    form: Tag = html.find("form", attrs=_FORM_ATTRS)
    if not form:
        raise RuntimeError(
            f"failed to find the form {_FORM_HTML}"
            f" on the Belorusneft page"
            f' "{settings.BELORUSNEFT_URL}"'
        )
    logger.debug(f"found form at: {form.sourceline}:{form.sourcepos}")

    return form


def transform_fuels(logger, form: Tag) -> Dict[Text, Text]:
    result = {}

    logger.debug(f"looking for all {_FUEL_CHECKBOX_HTML}")

    checkboxes = form.find_all("input", attrs=_FUEL_CHECKBOX_ATTRS)
    logger.debug(f"found {len(checkboxes)} checkboxes")

    for checkbox in checkboxes:
        checkbox_fuel_id = checkbox["value"]
        checkbox_fuel_name = checkbox.next.strip()
        logger.debug(f'found <checkbox value="{checkbox_fuel_id}">{checkbox_fuel_name}')

        fuel = BelorusneftFuel(checkbox_fuel_name)
        result[fuel.name] = checkbox_fuel_id
        logger.debug(f'mapped {fuel} -> checkbox "{checkbox_fuel_id}"')

    return result


def transform_currency(logger, form: Tag) -> Dict[Text, Text]:
    result = {}

    logger.debug(f"looking for all <option>")

    options = form.find_all("option")
    logger.debug(f"found {len(options)} options")

    for option in options:
        option_currency_name = option["value"]
        logger.debug(f'found <option value="{option_currency_name}">')

        currency = BelorusneftCurrency(option_currency_name)
        result[currency.name] = option_currency_name
        logger.debug(f'mapped {currency} -> option "{option_currency_name}"')

    return result


def transform_prices(logger, html: BeautifulSoup) -> Dict[date, Decimal]:
    logger.debug(f"looking for {_PRICES_TABLE_HTML}")

    table: Tag = html.find("table", attrs=_PRICES_TABLE_ATTRS)

    if not table:
        raise RuntimeError(
            f"failed to find a prices table {_PRICES_TABLE_HTML}"
            f" on the Belorusneft page"
            f' "{settings.BELORUSNEFT_URL}"'
        )
    logger.debug(f"found table at: {table.sourceline}:{table.sourcepos}")

    header = ()
    parsed_rows = []

    logger.debug(f"parsing table to get table rows <tr>")

    table_rows = table.find_all("tr")
    logger.debug(f"found {len(table_rows)} <tr>")

    for row_number, row in enumerate(table_rows):
        if row_number == 0:
            logger.debug(f"building header from <th>")

            header = tuple(th.text.strip() for th in row.find_all("th"))
            logger.debug(f"built header: {header}")

            if set(header) != _PRICES_TABLE_HEADER:
                raise RuntimeError(f"unexpected table header: {header}")

            continue

        cells = (td.text.strip() for td in row.find_all("td"))
        values = dict(zip(header, cells))
        logger.debug(
            f"built row {row_number:>4}: {json.dumps(values, indent=2, sort_keys=True)}"
        )

        parsed_rows.append(values)

    logger.debug(f"transforming price values to date->price map")

    prices = {
        datetime.strptime(row["Date"], "%d.%m.%Y"): Decimal(row["Price"])
        for row in parsed_rows
    }
    logger.debug(f"transformed {len(prices)} prices")

    return prices
