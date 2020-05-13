import asyncio
import json
from datetime import date
from decimal import Decimal
from typing import Dict

from aiohttp import ClientResponse
from dynaconf import settings

_PRICE_HISTORY_API = f"{settings.BENZAK_API_URL}/price-history/"


async def load_price(logger, session, price: Dict):
    logger.debug(
        f"calling Benzak price history API:"
        f' POST "{_PRICE_HISTORY_API}"'
        f" json={json.dumps(price, indent=2, sort_keys=True)}"
    )

    response: ClientResponse = await session.post(
        _PRICE_HISTORY_API,
        json=price,
        headers={"AUTHORIZATION": settings.BENZAK_API_TOKEN},
    )

    logger.debug(f"got response: [{response.status} {response.reason}]")
    if settings.DEBUG and response.status != 201:
        payload = json.dumps(await response.json(), indent=2, sort_keys=True)
        logger.debug(f"API response: {payload}")


async def load_prices(
    logger, session, prices: Dict[date, Decimal], currency: int, fuel: int
):
    logger.debug(
        f"loading prices"
        f" for currency={currency}, fuel={fuel}:"
        f" {len(prices)} prices"
    )

    logger.debug("creating tasks: load price")

    tasks = []
    for actual_at, price in prices.items():
        payload = {
            "at": actual_at.strftime("%Y-%m-%d"),
            "price": str(price),
            "currency": currency,
            "fuel": fuel,
        }

        task = asyncio.create_task(load_price(logger, session, payload))
        tasks.append(task)
    logger.debug(f"created {len(tasks)} tasks")

    logger.debug("awaiting tasks: load price")

    for task in tasks:
        await task
    logger.debug(f"loaded {len(prices)} prices")
