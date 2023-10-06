from fastapi import FastAPI


def init_api(app: FastAPI):
    from . import short_url

    app.include_router(short_url.router, prefix="/api")
