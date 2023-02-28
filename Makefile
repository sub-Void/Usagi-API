#!/usr/bin/make

include .env

help:
	@echo "make"
	@echo "    install"
	@echo "        Install all packages of poetry project locally without dev dependencies."
	@echo "    install-dev"
	@echo "        Install all packages of poetry project locally."
	@echo "    run-dev"
	@echo "        Run development docker compose."
	@echo "    run-prod"
	@echo "        Run production server."
	@echo "    stop-prod"
	@echo "        Stop production server."
	@echo "    init-db"
	@echo "        Init database and sample data."	
	@echo "    generate-migration"
	@echo "        Generate new database migration using alembic."
	@echo "    shell"
	@echo "        Opens an interactive python shell in the context of app:main"

install-dev:
	python3 -m venv venv --prompt $(PROJECT_NAME) && \
	source ./venv/bin/activate && \
	pip install --upgrade pip setuptools wheel && \
	pip install -e ."[dev]"

run-dev:
	uvicorn app.main:app --reload

run-prod:
	echo 'Coming soon'

init-db:
	python app/init_db.py

add-dev-migration:
	alembic revision --autogenerate && \
	alembic upgrade head

shell:
	python3 -i app/main.py