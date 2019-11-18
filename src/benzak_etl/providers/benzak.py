from typing import Dict, Text

import requests
from dynaconf import settings

from benzak_etl.consts import BenzakCurrency, BenzakFuel

_FUEL_API = f"{settings.BENZAK_API_URL}/fuel/"
_CURRENCY_API = f"{settings.BENZAK_API_URL}/currency/"


def build_fuel_map(logger) -> Dict[Text, int]:
    response = requests.get(_FUEL_API)

    msg = f'GET "{_FUEL_API}" -> {response}'
    logger.debug(f"calling Benzak fuel API: {msg}")

    if response.status_code != 200:
        raise RuntimeError(f"failed to get fuels from Benzak API: {msg}")

    payload = response.json()
    logger.debug(f"got response payload: {len(payload)} objects")

    logger.debug(f"parsing fuels from payload")

    fuel_map = {BenzakFuel(fuel["name"]).name: fuel["id"] for fuel in payload}
    logger.debug(f"mapped {len(fuel_map)} fuels")

    return fuel_map


def build_currency_map(logger) -> Dict[Text, int]:
    response = requests.get(_CURRENCY_API)

    msg = f'GET "{_CURRENCY_API}" -> {response}'
    logger.debug(f"calling Benzak currency API: {msg}")

    if response.status_code != 200:
        raise RuntimeError(f"failed to get currency from Benzak API: {msg}")

    payload = response.json()
    logger.debug(f"got response payload: {len(payload)} objects")

    logger.debug(f"parsing currencies from payload")

    currency_map = {
        BenzakCurrency(currency["name"]).name: currency["id"] for currency in payload
    }
    logger.debug(f"mapped {len(currency_map)} currencies")

    return currency_map
