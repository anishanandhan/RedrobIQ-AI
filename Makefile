.PHONY: lint typecheck test test-cov all

lint:
	venv/bin/ruff check .

typecheck:
	venv/bin/mypy .

test:
	venv/bin/python -m pytest

test-cov:
	venv/bin/python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=60

all: lint typecheck test-cov
