import asyncio
import logging
from datetime import date, timedelta
from random import randint
from typing import List

import aiohttp
from dynaconf import settings

from benzak_etl.consts import Currency, ExtractTask, Fuel
from benzak_etl.load import load_prices
from benzak_etl.providers import belorusneft, benzak
from custom_logging import configure_logging


async def extract_src_identities(logger, session):
    logger.debug("extracting html with form from Belorusneft")

    html = await belorusneft.extract_html(logger, session)
    logger.debug("extracted html")

    logger.debug("looking for form in html")

    form = belorusneft.extract_form(logger, html)
    logger.debug("found form")

    logger.debug("transforming fuels identities into map")

    fuels = belorusneft.transform_fuels(logger, form)
    logger.debug("transformed fuels")

    logger.debug("transforming currency identities into map")

    currency = belorusneft.transform_currency(logger, form)
    logger.debug("transformed currency")

    return currency, fuels


async def extract_dst_identities(logger, session):
    logger.debug("extracting fuel map: creating tasks")

    task_fuels = asyncio.create_task(benzak.extract_fuels(logger, session))
    task_currency = asyncio.create_task(benzak.extract_currency(logger, session))
    logger.debug("created tasks")

    logger.debug("awaiting fuels task")

    fuels = await task_fuels
    logger.debug("got fuels map")

    logger.debug("awaiting currency task")

    currency = await task_currency
    logger.debug("got currency map")

    return currency, fuels


def extract_prices(logger, session, fuels_map, currency_map) -> List[ExtractTask]:
    tasks = []

    date_to = date.today()
    date_from = date_to - timedelta(days=randint(7, 14))
    if settings.FULL_LOAD:
        date_from = date(year=2016, month=7, day=1)
        logger.warning("performing a FULL LOAD")

    logger.debug(
        f"using dates:"
        f" {date_from.strftime('%Y-%m-%d')}~{date_to.strftime('%Y-%m-%d')}"
    )

    for fuel in Fuel:
        logger.debug(f"using fuel {fuel}")

        fuel_id = fuels_map.get(fuel.name)
        if not fuel_id:
            logger.warning(f"fuel {fuel.name} not found on source, skipping")
            continue

        for currency in Currency:
            logger.debug(f"using currency {currency} (still {fuel})")

            currency_id = currency_map.get(currency.name)
            if not currency_id:
                logger.warning(
                    f"currency {currency.name} not found on source, skipping"
                )
                continue

            task = ExtractTask(
                task=asyncio.create_task(
                    belorusneft.extract_html(
                        logger,
                        session,
                        date_from=date_from,
                        date_to=date_to,
                        currency_id=currency_id,
                        fuel_id=fuel_id,
                    )
                ),
                fuel=fuel,
                currency=currency,
            )

            logger.debug(f"created task")

            tasks.append(task)

    return tasks


async def etl(session):
    logger = logging.getLogger("etl")

    logger.debug("creating tasks: extract identities")

    task_src = asyncio.create_task(extract_src_identities(logger, session))
    task_dst = asyncio.create_task(extract_dst_identities(logger, session))
    logger.debug("created tasks: extract identities")

    logger.debug("awaiting tasks: extract identities")

    src_currency, src_fuels = await task_src
    dst_currency, dst_fuels = await task_dst
    logger.debug("got identities maps")

    logger.debug("creating extract tasks")

    tasks_extract = extract_prices(logger, session, src_fuels, src_currency)
    logger.debug(f"created {len(tasks_extract)} tasks: extract prices")

    logger.debug("creating tasks: load")

    tasks_load = []

    for task_n, task_extract in enumerate(tasks_extract):
        logger.debug(
            f"#{task_n}: extracting prices for"
            f" {task_extract.fuel}, {task_extract.currency}"
        )

        html = await task_extract.task
        logger.debug(f"#{task_n}: extracted html: {len(html)} tags")

        logger.debug(f"#{task_n}: transforming prices")

        prices = belorusneft.transform_prices(logger, html)
        logger.debug(f"#{task_n}: transformed prices: {len(prices)}")

        logger.debug(
            f"#{task_n}: creating load task for"
            f" {task_extract.fuel}, {task_extract.currency}"
        )

        task_load = asyncio.create_task(
            load_prices(
                logger,
                session,
                prices,
                dst_currency[task_extract.currency.name],
                dst_fuels[task_extract.fuel.name],
            )
        )
        tasks_load.append(task_load)
        logger.debug(
            f"#{task_n}: created load task for"
            f" {task_extract.fuel} / {task_extract.currency}"
        )

    logger.debug("awaiting load tasks")

    for task_n, task_load in enumerate(tasks_load):
        logger.debug(f"#{task_n}: awaiting load task")
        await task_load
        logger.debug(f"#{task_n}: completed load task")

    logger.debug("loaded prices")


async def run_etl():
    async with aiohttp.ClientSession() as session:
        await etl(session)


if __name__ == "__main__":
    configure_logging()
    _LOOP = asyncio.get_event_loop()
    _LOOP.run_until_complete(run_etl())
