from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.contrib.fastapi import register_tortoise

from base.error_handlers import (
    app_exception_handler,
    http_exception_handler,
    pydantic_validation_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from base.exceptions import AppException
from base.logging import setup_logging
from base.settings import TORTOISE_ORM
from notification.router import notification_router
from user.router import auth_router

setup_logging()

app = FastAPI(redoc_url=None)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(notification_router, prefix="/notifications", tags=["notifications"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
