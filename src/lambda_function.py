import asyncio

from custom_logging import configure_logging
from main import run_etl


def lambda_handler(_event, _context):
    configure_logging()
    _LOOP = asyncio.get_event_loop()
    _LOOP.run_until_complete(run_etl())
