import logging

from dynaconf import settings


def configure_logging():
    logging.basicConfig(
        format="{asctime}\t[{name}:{levelname}] {module}.{funcName}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
    )
