import json
from datetime import date
from decimal import Decimal
from typing import Dict

from dynaconf import settings

_PRICE_HISTORY_API = f"{settings.BENZAK_API_URL}/price-history/"


async def save_price(logger, session, price: Dict):
    logger.debug(
        f"calling Benzak price history API:"
        f' POST "{_PRICE_HISTORY_API}"'
        f" json={json.dumps(price, indent=2, sort_keys=True)}"
    )

    response = await session.post(
        _PRICE_HISTORY_API,
        json=price,
        headers={"AUTHORIZATION": settings.BENZAK_API_TOKEN},
    )
    logger.debug(f"got response: {response}")


async def save_prices(
    logger, session, prices: Dict[date, Decimal], currency: int, fuel: int
):
    logger.debug(
        f"saving prices"
        f" for currency={currency}, fuel={fuel}:"
        f" {len(prices)} prices"
    )

    for actual_at, price in prices.items():
        payload = {
            "at": actual_at.strftime("%Y-%m-%d"),
            "price": str(price),
            "currency": currency,
            "fuel": fuel,
        }

        await save_price(logger, session, payload)

    logger.debug(f"saved {len(prices)} prices")
