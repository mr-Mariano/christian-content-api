.PHONY: install up down logs run-api reset-db seed reseed

PYTHON=.venv/bin/python
PIP=.venv/bin/pip
GUNICORN=.venv/bin/gunicorn

install:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

run-api:
	$(GUNICORN) --bind 0.0.0.0:8000 app:app

reset-db:
	$(PYTHON) cli.py reset

seed:
	$(PYTHON) seed_data.py

reseed:
	$(PYTHON) seed_data.py
