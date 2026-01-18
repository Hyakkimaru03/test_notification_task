import logging
from typing import Any, Dict

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import (
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from base.exceptions import AppException

logger = logging.getLogger("app")


def _error_payload(
    code: str, message: str, details: Any | None = None, request_id: str | None = None
) -> Dict[str, Any]:
    error: Dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    if request_id:
        error["request_id"] = request_id
    return {"error": error}


def _request_id(request: Request) -> str | None:
    return request.headers.get("X-Request-ID")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    payload = _error_payload(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=exc.status_code, content=payload)


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    payload = _error_payload(
        code=f"http_{exc.status_code}",
        message=message,
        details=None if isinstance(exc.detail, str) else exc.detail,
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=exc.status_code, content=payload)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    payload = _error_payload(
        code="validation_error",
        message="Validation error",
        details=exc.errors(),
        request_id=_request_id(request),
    )
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload,
    )


async def pydantic_validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    payload = _error_payload(
        code="validation_error",
        message="Validation error",
        details=exc.errors(),
        request_id=_request_id(request),
    )
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", extra={"path": request.url.path})
    payload = _error_payload(
        code="internal_error",
        message="Internal server error",
        request_id=_request_id(request),
    )
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=payload,
    )
