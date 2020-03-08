#!/usr/bin/env bash

# ---------------------------------------------------------
abort() {
  if test -n "$1"; then
    echo >&2 -e "\n\nFAILED: $1\n\n"
  fi
  exit 1
}

trap 'abort' 0

set -e
set -o pipefail

# ---------------------------------------------------------

# checks

export ENV_FOR_DYNACONF=testing

PYTHONPATH=src pipenv run pytest
pipenv run black --check . || abort "BLACK IS NOT HAPPY"
pipenv run flake8 || abort "FLAKE8 IS NOT HAPPY"
pipenv run pylint ./src/ || abort "PYLINT IS NOT HAPPY"

# ---------------------------------------------------------
trap : 0
# ---------------------------------------------------------
