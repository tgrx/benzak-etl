from dynaconf import settings


def main():
    print(f"denv: {settings.ENV_FOR_DYNACONF}")
    print(f"debug: {settings.DEBUG}")


if __name__ == "__main__":
    main()
