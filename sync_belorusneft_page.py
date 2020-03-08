from pathlib import Path

import requests
from dynaconf import settings


def main():
    here = Path(__file__).parent.resolve()
    assert here.is_dir()

    page = requests.get(settings.BELORUSNEFT_URL)
    assert page

    test_page = here / "tests" / "belorusneft_prices.html"

    with test_page.open("w") as dst:
        dst.write(page.text)

    return len(page.text)


if __name__ == "__main__":
    print(main())
