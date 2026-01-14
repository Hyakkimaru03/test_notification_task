from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from base.settings import COOKIE_DOMAIN, DEBUG


class AuthCleanupMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if response.status_code == 401:
            response.delete_cookie(
                key="access_token",
                domain=COOKIE_DOMAIN if not DEBUG else None,
                path="/",
            )
        elif response.status_code == 402:
            response.delete_cookie(
                key="refresh_token",
                domain=COOKIE_DOMAIN if not DEBUG else None,
                path="/",
            )
        return response
