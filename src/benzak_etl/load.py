import json
from datetime import date
from decimal import Decimal
from typing import Dict

import requests
from dynaconf import settings

_PRICE_HISTORY_API = f"{settings.BENZAK_API_URL}/price-history/"


def save_price(logger, price: Dict):
    logger.debug(
        f'calling Benzak price history API: POST "{_PRICE_HISTORY_API}" json={json.dumps(price, indent=2, sort_keys=True)}'
    )

    response = requests.post(
        _PRICE_HISTORY_API,
        json=price,
        headers={"AUTHORIZATION": settings.BENZAK_API_TOKEN},
    )
    logger.debug(f"got response: {response}")


def save_prices(logger, prices: Dict[date, Decimal], currency: int, fuel: int):
    logger.debug(
        f"saving prices for currency={currency}, fuel={fuel}: {len(prices)} prices"
    )

    for actual_at, price in prices.items():
        payload = {
            "at": actual_at.strftime("%Y-%m-%d"),
            "price": str(price),
            "currency": currency,
            "fuel": fuel,
        }

        save_price(logger, payload)

    logger.debug(f"saved {len(prices)} prices")
