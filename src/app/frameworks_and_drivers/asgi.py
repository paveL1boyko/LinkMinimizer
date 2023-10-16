import logging

from app.adapters.api.endpoints import init_api
from app.adapters.cache.redis_cache import init_redis_cache
from app.adapters.db.mongo_db import mongo_client
from fastapi import Depends, FastAPI

logging.basicConfig(level=logging.INFO)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """Initialize Redis cache and MongoDB client at startup."""
    init_redis_cache()


@app.on_event("shutdown")
async def shutdown_event(client: Depends = Depends(mongo_client)):
    """Close MongoDB client connection at shutdown."""
    logging.info("Closing MongoDB client...")
    if client:
        client.close()


logging.info("Initializing API endpoints...")
init_api(app)
