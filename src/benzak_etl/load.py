from datetime import date
from decimal import Decimal
from typing import Dict

import requests
from dynaconf import settings


def save_price(logger, price: Dict):
    logger.debug("sending POST to benzak api")
    url = f"{settings.BENZAK_API_URL}/price-history/"
    response = requests.post(
        url, json=price, headers={"AUTHORIZATION": settings.BENZAK_API_TOKEN}
    )
    logger.debug(f"POST completed: {response}")


def save_prices(logger, prices: Dict[date, Decimal], currency: int, fuel: int):
    logger.debug(f"saving prices for currency={currency}, fuel={fuel}")
    for actual_at, price in prices.items():
        logger.debug(f"saving: at={actual_at.strftime('%Y-%m-%d')}, price={price!s}")
        payload = {
            "at": actual_at.strftime("%Y-%m-%d"),
            "price": str(price),
            "currency": currency,
            "fuel": fuel,
        }

        save_price(logger, payload)
