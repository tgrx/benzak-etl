from functools import wraps

from dynaconf import settings


def configure_sentry():
    if settings.DEBUG:
        return

    # pylint:disable=C0415  # non-top-level import
    import sentry_sdk

    sentry_sdk.init(settings.SENTRY_DSN)


def safe(func):
    if settings.DEBUG:
        return func

    @wraps(func)
    def _safe_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        # pylint:disable=W0703  # broad exception
        except Exception as err:
            # pylint:disable=C0415  # non-top-level import
            from sentry_sdk import capture_exception

            capture_exception(err)
            result = None

        return result

    return _safe_func
