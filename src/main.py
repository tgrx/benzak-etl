import logging
from datetime import date, timedelta

from benzak_etl.consts import Currency, Fuel
from benzak_etl.load import save_prices
from benzak_etl.providers import belorusneft, benzak
from custom_logging import configure_logging


def build_src_maps(logger):
    logger.debug("fetching html with form from Belorusneft")

    html = belorusneft.get_html(logger)
    logger.debug("fetched html")

    logger.debug("looking for form in html")

    form = belorusneft.get_form(logger, html)
    logger.debug("found form")

    logger.debug("building fuel map")

    fuels = belorusneft.build_fuel_map(logger, form)
    logger.debug("built fuel map")

    logger.debug("building currency map")

    currency = belorusneft.build_currency_map(logger, form)
    logger.debug("built currency map")

    return currency, fuels


def build_dst_maps(logger):
    logger.debug("building fuel map")

    fuels = benzak.build_fuel_map(logger)
    logger.debug("built fuel map")

    logger.debug("building currency map")

    currency = benzak.build_currency_map(logger)
    logger.debug("built currency map")

    return currency, fuels


def main():
    logger = logging.getLogger("etl")

    logger.debug("building maps")

    src_currency, src_fuels = build_src_maps(logger)
    dst_currency, dst_fuels = build_dst_maps(logger)
    logger.debug("built maps")

    for fuel in Fuel:
        logger.debug(f"using fuel {fuel}")

        for currency in Currency:
            logger.debug(f"using currency {currency} (still {fuel})")

            logger.debug(f"fetching html with prices from Belorusneft")

            # date(year=2016, month=7, day=1),

            date_to = date.today()
            date_from = date_to - timedelta(days=7)

            html = belorusneft.get_html(
                logger,
                date_from=date_from,
                date_to=date_to,
                currency_id=src_currency[currency.name],
                fuel_id=src_fuels[fuel.name],
            )
            logger.debug(f"fetched html")

            logger.debug(f"building prices from html")

            prices = belorusneft.get_prices(logger, html)
            logger.debug(f"built prices")

            logger.debug(f"saving prices into Benzak")

            save_prices(
                logger, prices, dst_currency[currency.name], dst_fuels[fuel.name]
            )
            logger.debug(f"saved prices")


if __name__ == "__main__":
    configure_logging()
    main()
