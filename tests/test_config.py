from dynaconf import settings

MANDATORY_CONFIG_ARGS = {
    "BELORUSNEFT_URL",
    "BENZAK_API_TOKEN",
    "BENZAK_API_URL",
    "DEBUG",
}


def test_config():
    assert settings.ENV_FOR_DYNACONF == "testing"

    for arg in MANDATORY_CONFIG_ARGS:
        assert hasattr(settings, arg)

    assert settings.BELORUSNEFT_URL == "tests/belorusneft_prices.html"
    assert settings.BENZAK_API_TOKEN is None
    assert settings.BENZAK_API_URL == "https://benzak.herokuapp.com/api/v1"
    assert settings.DEBUG is False
