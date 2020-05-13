from typing import Dict
from typing import Text

from aiohttp import ClientResponse
from dynaconf import settings

from benzak_etl.consts import BenzakCurrency
from benzak_etl.consts import BenzakFuel

_FUEL_API = f"{settings.BENZAK_API_URL}/fuel/"
_CURRENCY_API = f"{settings.BENZAK_API_URL}/currency/"


async def extract_fuels(logger, session) -> Dict[Text, int]:
    logger.debug(f"calling Benzak fuel API: {_FUEL_API}")

    response: ClientResponse = await session.get(_FUEL_API)
    logger.debug(f"got response: {response.status} {response.reason}")

    if response.status != 200:
        raise RuntimeError(f"failed to get fuels from Benzak API: {response}")

    payload = await response.json()
    logger.debug(f"got response payload: {len(payload)} objects")

    logger.debug("transforming fuel identities into map")

    fuel_map = {BenzakFuel(fuel["name"]).name: fuel["id"] for fuel in payload}
    logger.debug(f"transformed {len(fuel_map)} fuels")

    return fuel_map


async def extract_currency(logger, session) -> Dict[Text, int]:
    logger.debug(f"calling Benzak currency API: {_CURRENCY_API}")

    response: ClientResponse = await session.get(_CURRENCY_API)
    logger.debug(f"got response: {response.status} {response.reason}")

    if response.status != 200:
        raise RuntimeError(f"failed to get currency from Benzak API: {response}")

    payload = await response.json()
    logger.debug(f"got response payload: {len(payload)} objects")

    logger.debug("transforming currency identities into map")

    currency_map = {
        BenzakCurrency(currency["name"]).name: currency["id"] for currency in payload
    }
    logger.debug(f"transformed {len(currency_map)} currency")

    return currency_map
