from pathlib import Path

import pytest

_belorusneft_prices_page_html = None

_here = Path(__file__).parent.resolve()
assert _here.is_dir()


@pytest.fixture
def belorusneft_prices_page():
    global _belorusneft_prices_page_html
    if _belorusneft_prices_page_html:
        return _belorusneft_prices_page_html

    page_file = _here / "belorusneft_prices.html"

    with page_file.open("r") as src:
        _belorusneft_prices_page_html = src.read()

    return _belorusneft_prices_page_html
