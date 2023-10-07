import logging

from app.adapters.api.endpoints import init_api
from app.adapters.cache.redis_cache import init_redis_cache
from app.adapters.db.mongo_db import init_short_url_db
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Initialize MongoDB client and collection as None
client: AsyncIOMotorClient | None = None
short_link_collection: AsyncIOMotorCollection = None


@app.on_event("startup")
async def startup_event():
    """Initialize Redis cache and MongoDB client at startup."""
    global client, short_link_collection

    init_redis_cache()

    client, db, short_link_collection = await init_short_url_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB client connection at shutdown."""
    global client

    logging.info("Closing MongoDB client...")
    if client:
        client.close()


logging.info("Initializing API endpoints...")
init_api(app)
