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

DATABASE_URL = os.getenv('DATABASE_URL', "postgres://test_user:testpassword@postgres:5432/test_db")

TORTOISE_ORM = {
    "connections": {
        "default": DATABASE_URL},
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
