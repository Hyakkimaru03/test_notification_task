from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AppException(Exception):
    code: str
    message: str
    status_code: int = 400
    details: Optional[Any] = None


class BadRequestError(AppException):
    def __init__(self, code: str, message: str, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=400, details=details)


class UnauthorizedError(AppException):
    def __init__(self, code: str, message: str, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=401, details=details)


class ForbiddenError(AppException):
    def __init__(self, code: str, message: str, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=403, details=details)


class NotFoundError(AppException):
    def __init__(self, code: str, message: str, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=404, details=details)


class ConflictError(AppException):
    def __init__(self, code: str, message: str, details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=409, details=details)
