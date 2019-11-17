from dynaconf import settings


def test_config():
    assert settings.ENV_FOR_DYNACONF == "testing"
    assert settings.DEBUG is False
