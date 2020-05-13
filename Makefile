HERE := $(shell pwd)
VENV := $(shell pipenv --venv)
PYTHONPATH := ${HERE}/src


ifeq ($(origin PIPENV_ACTIVE), undefined)
	RUN := pipenv run
endif

ifeq ($(ENV_FOR_DYNACONF), travis)
	RUN :=
endif


.PHONY: format
format:
	${RUN} isort --virtual-env ${VENV} --recursive --apply ${HERE}
	${RUN} black ${HERE}


.PHONY: run
run:
	PYTHONPATH="${PYTHONPATH}" ${RUN} python -m main


.PHONY: test
test:
	ENV_FOR_DYNACONF=testing PYTHONPATH="${PYTHONPATH}" ${RUN} coverage run -m pytest
	${RUN} coverage report
	${RUN} isort --virtual-env ${VENV} --recursive --check-only "${HERE}/src"
	${RUN} black --check "${HERE}/src"
	${RUN} flake8 "${HERE}/src"
	${RUN} pylint "${HERE}/src"


.PHONY: report
report:
	${RUN} coverage html --directory=${HERE}/htmlcov --fail-under=0
	open "${HERE}/htmlcov/index.html"


.PHONY: venv
venv:
	pipenv install --dev


.PHONY: clean
clean:
	${RUN} coverage erase
	rm -rf .pytest_cache
	rm -rf .serverless
	rm -rf htmlcov
	rm -rf node_modules
	find . -type d -name "__pycache__" | xargs rm -rf


.PHONY: lambda
lambda:
	sls deploy
