JWT токены передаются через headers (Authorization: Bearer).

## First Start (Docker)

```bash
docker compose up -d postgres redis
docker compose run --rm aerich aerich init -t app.base.settings.TORTOISE_ORM
docker compose run --rm aerich aerich init-db
docker compose up -d fastapi
```

## Via make

```make init```

## Simple Start

docker compose up -d

## Tests

Local tests (uses temp SQLite DB for tests):

```bash
make test # if venv using
```

Docker tests (if you want to run inside the container):

```bash
docker compose run --rm fastapi pytest
```

## Pre-commit

```bash
pre-commit install
make pre-commit
```

## Linters / Formatters

```bash
black .
isort .
flake8 . --exclude .venv,__pycache__,migrations
```

## Project layout

- `app/` - application code
- `app/tests/` - tests
- `docker-compose.yml` - services (fastapi, postgres, redis, aerich)
- `Makefile` - shortcuts
