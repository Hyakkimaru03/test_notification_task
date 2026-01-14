# ----------------------------
# DOCKER SHORTCUTS
# ----------------------------

init:
	@docker compose up -d postgres redis
	@docker compose run --rm aerich aerich init -t app.base.settings.TORTOISE_ORM
	@docker compose run --rm aerich aerich init-db
	@docker compose up -d fastapi

re-build:
	docker compose up -d --build fastapi

migrate-up:
	docker compose run --rm aerich aerich migrate && \
	docker compose run --rm aerich aerich upgrade

test:
	cd app && pytest

pre-commit:
	pre-commit run --all-files
