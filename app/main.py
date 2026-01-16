import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from base.settings import PORT, RELOAD, TORTOISE_ORM, WORKERS
from notification.router import notification_router
from user.router import auth_router

logger = logging.getLogger(__name__)

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

app.include_router(notification_router, prefix="/notifications", tags=["notifications"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=RELOAD, workers=WORKERS)
