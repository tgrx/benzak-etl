import logging
from datetime import date

from benzak_etl.consts import Currency, Fuel
from benzak_etl.load import save_prices
from benzak_etl.providers import belorusneft, benzak
from custom_logging import configure_logging


def build_src_maps(logger):
    logger.debug("building src maps")
    html = belorusneft.get_html(logger)
    form = belorusneft.get_form(logger, html)

    fuels = belorusneft.get_fuel_map(logger, form)
    currency = belorusneft.get_currency_map(logger, form)
    logger.debug("src maps are built")

    return currency, fuels


def build_dst_maps(logger):
    logger.debug("building dst maps")
    fuels = benzak.get_fuel_map(logger)
    currency = benzak.get_currency_map(logger)
    logger.debug("dst maps are built")

    return currency, fuels


def main():
    logger = logging.getLogger("etl")
    src_currency, src_fuels = build_src_maps(logger)
    dst_currency, dst_fuels = build_dst_maps(logger)

    for fuel in Fuel:
        for currency in Currency:
            html = belorusneft.get_html(
                logger,
                date_from=date(year=2016, month=7, day=1),
                date_to=date.today(),
                currency_id=src_currency[currency.name],
                fuel_id=src_fuels[fuel.name],
            )

            prices = belorusneft.get_prices(logger, html)

            save_prices(
                logger, prices, dst_currency[currency.name], dst_fuels[fuel.name]
            )

            break
        break


if __name__ == "__main__":
    configure_logging()
    main()
