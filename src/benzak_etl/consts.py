import enum
from typing import Awaitable
from typing import NamedTuple


@enum.unique
class Fuel(enum.Enum):
    BN_92 = "BN_92"
    DT_A = "DT_A"
    DT_E5 = "DT_E5"
    LPG = "LPG"
    RON_92 = "RON_92"
    RON_95 = "RON_95"
    RON_98 = "RON_98"


@enum.unique
class Currency(enum.Enum):
    BYN = "BYN"
    EUR = "EUR"
    RUB = "RUB"
    USD = "USD"


@enum.unique
class BenzakFuel(enum.Enum):
    BN_92 = "BN-92"
    DT_A = "DT-ARCTIC"
    DT_E5 = "DT-E5"
    LPG = "LPG"
    RON_92 = "RON-92"
    RON_95 = "RON-95"
    RON_98 = "RON-98"


assert {i.value for i in Fuel} == {i.name for i in BenzakFuel}


@enum.unique
class BelorusneftFuel(enum.Enum):
    BN_92 = "BN-92"
    DT_A = "Diesel -32°C"
    DT_E5 = "Diesel Euro 5"
    LPG = "LPG *"
    RON_92 = "92 RON"
    RON_95 = "95 RON"
    RON_98 = "98 RON"


assert {i.value for i in Fuel} == {i.name for i in BelorusneftFuel}


@enum.unique
class BelorusneftCurrency(enum.Enum):
    BYN = "byr"
    EUR = "eur"
    RUB = "rub"
    USD = "usd"


assert {i.value for i in Currency} == {i.name for i in BelorusneftCurrency}


@enum.unique
class BenzakCurrency(enum.Enum):
    BYN = "BYN"
    EUR = "EUR"
    RUB = "RUB"
    USD = "USD"


assert {i.value for i in Currency} == {i.name for i in BenzakCurrency}


class ExtractTask(NamedTuple):
    task: Awaitable
    fuel: Fuel
    currency: Currency
