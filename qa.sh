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
SRC_DIR="./src/"

PYTHONPATH=src pipenv run pytest
pipenv run black --check "${SRC_DIR}" || abort "BLACK IS NOT HAPPY"
pipenv run flake8 "${SRC_DIR}" || abort "FLAKE8 IS NOT HAPPY"
pipenv run pylint "${SRC_DIR}" || abort "PYLINT IS NOT HAPPY"

# ---------------------------------------------------------
trap : 0
# ---------------------------------------------------------
