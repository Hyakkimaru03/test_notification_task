import os

import redis.asyncio as aioredis
from dotenv import load_dotenv

load_dotenv()

DEBUG = bool(os.getenv("DEBUG"))

if DEBUG:
    DOMAIN_NAME = "127.0.0.1:8000"
    COOKIE_DOMAIN = f".{DOMAIN_NAME}"
    WORKERS = 1
    RELOAD = True
else:
    DOMAIN_NAME = "127.0.0.1:8000"
    COOKIE_DOMAIN = f".{DOMAIN_NAME}"
    RELOAD = False
    WORKERS = 2

PORT = 8000
JWT_SECRET = os.getenv("JWT_SECRET", "test")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

POSTGRES_USER = os.getenv('POSTGRES_USER', 'test_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'test_password')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'test_db')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 5432)

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"},
    "apps": {
        "models": {
            "models": [
                "aerich.models",
                "user.models",
                "notification.models",
            ],
            "default_connection": "default",
        }
    },
    "timezone": "UTC",
    "use_tz": True,
}

redis = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
