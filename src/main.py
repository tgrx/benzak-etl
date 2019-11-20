import asyncio
import logging
from datetime import date
from typing import List

import aiohttp

from benzak_etl.consts import Currency, ExtractTask, Fuel
from benzak_etl.load import save_prices
from benzak_etl.providers import belorusneft, benzak
from custom_logging import configure_logging


async def build_src_maps(logger, session):
    logger.debug("fetching html with form from Belorusneft")

    html = await belorusneft.get_html(logger, session)
    logger.debug("fetched html")

    logger.debug("looking for form in html")

    form = belorusneft.get_form(logger, html)
    logger.debug("found form")

    logger.debug("building fuel map")

    fuels = belorusneft.build_fuel_map(logger, form)
    logger.debug("built fuel map")

    logger.debug("building currency map")

    currency = belorusneft.build_currency_map(logger, form)
    logger.debug("built currency map")

    return currency, fuels


async def build_dst_maps(logger, session):
    logger.debug("building fuel map: creating tasks")

    fuels_task = asyncio.create_task(benzak.build_fuel_map(logger, session))
    currency_task = asyncio.create_task(benzak.build_currency_map(logger, session))
    logger.debug("created tasks")

    logger.debug("awaiting fuels task")

    fuels = await fuels_task
    logger.debug("got fuels map")

    logger.debug("awaiting currency task")

    currency = await currency_task
    logger.debug("got currency map")

    return currency, fuels


def create_extract_tasks(logger, session, fuels_map, currency_map) -> List[ExtractTask]:
    tasks = []

    for fuel in Fuel:
        logger.debug(f"using fuel {fuel}")

        fuel_id = fuels_map[fuel.name]

        for currency in Currency:
            logger.debug(f"using currency {currency} (still {fuel})")

            currency_id = currency_map[currency.name]

            date_to = date.today()
            date_from = date(year=2016, month=7, day=1)

            logger.debug(
                f"using dates:"
                f" {date_from.strftime('%Y-%m-%d')}~{date_to.strftime('%Y-%m-%d')}"
            )

            task = ExtractTask(
                task=asyncio.create_task(
                    belorusneft.get_html(
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


async def main(session):
    logger = logging.getLogger("etl")

    logger.debug("creating map tasks")

    src_map_task = asyncio.create_task(build_src_maps(logger, session))
    dst_map_task = asyncio.create_task(build_dst_maps(logger, session))
    logger.debug("created map tasks")

    logger.debug("awaiting map tasks")

    src_currency, src_fuels = await src_map_task
    dst_currency, dst_fuels = await dst_map_task
    logger.debug("got maps")

    logger.debug("creating extract tasks")

    extract_tasks = create_extract_tasks(logger, session, src_fuels, src_currency)
    logger.debug(f"created extract tasks: {len(extract_tasks)}")

    logger.debug("creating load tasks")

    load_tasks = []

    for task_n, extract_task in enumerate(extract_tasks):
        logger.debug(
            f"#{task_n}: extracting prices for"
            f" {extract_task.fuel} / {extract_task.currency}"
        )

        html = await extract_task.task
        logger.debug(f"#{task_n}: extracted html: {len(html)} tags")

        logger.debug(f"#{task_n}: parsing prices from task")

        prices = belorusneft.get_prices(logger, html)
        logger.debug(f"#{task_n}: parsed prices: {len(prices)}")

        logger.debug(
            f"#{task_n}: creating load task for"
            f" {extract_task.fuel} / {extract_task.currency}"
        )

        load_task = asyncio.create_task(
            save_prices(
                logger,
                session,
                prices,
                dst_currency[extract_task.currency.name],
                dst_fuels[extract_task.fuel.name],
            )
        )
        load_tasks.append(load_task)
        logger.debug(
            f"#{task_n}: created load task for"
            f" {extract_task.fuel} / {extract_task.currency}"
        )

    logger.debug("awaiting load tasks")

    for task_n, load_task in enumerate(load_tasks):
        logger.debug(f"#{task_n}: awaiting load task")
        await load_task
        logger.debug(f"#{task_n}: completed load task")

    logger.debug("saved prices")


async def run_main():
    async with aiohttp.ClientSession() as session:
        await main(session)


if __name__ == "__main__":
    configure_logging()
    _LOOP = asyncio.get_event_loop()
    _LOOP.run_until_complete(run_main())
