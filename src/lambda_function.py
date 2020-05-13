import asyncio

from custom_logging import configure_logging
from main import run_etl
from safeguards import configure_sentry


def lambda_handler(_event, _context):
    configure_logging()
    configure_sentry()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_etl())
