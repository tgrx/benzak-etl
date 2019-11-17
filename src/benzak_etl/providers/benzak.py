from typing import Dict, Text

import requests
from dynaconf import settings

from benzak_etl.consts import BenzakCurrency, BenzakFuel


def get_fuel_map(logger) -> Dict[Text, int]:
    logger.debug("building fuel map")

    url = f"{settings.BENZAK_API_URL}/fuel/"
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(
            f'failed to get fuels from Benzak API: GET "{url}" -> {response}'
        )

    payload = response.json()

    return {BenzakFuel(fuel["name"]).name: fuel["id"] for fuel in payload}


def get_currency_map(logger) -> Dict[Text, int]:
    logger.debug("building fuel map")

    url = f"{settings.BENZAK_API_URL}/currency/"
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(
            f'failed to get currency from Benzak API: GET "{url}" -> {response}'
        )

    payload = response.json()

    return {
        BenzakCurrency(currency["name"]).name: currency["id"] for currency in payload
    }
