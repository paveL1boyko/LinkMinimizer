from app.adapters.api.endpoints import init_api
from app.adapters.cache.redis_cache import init_redis_cache
from app.core.config import Config
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

client: AsyncIOMotorClient = None
short_link_collection = None


@app.on_event("startup")
async def startup_event():
    global client, short_link_collection
    init_redis_cache()
    client = AsyncIOMotorClient(Config.MONGODB_DB_URL)

    db = client[Config.LINK_MINIMIZER_DB_NAME]
    short_link_collection = db.short_urls
    await short_link_collection.create_index("short_code", unique=True)


@app.on_event("shutdown")
async def shutdown_event():
    if client:
        await client.close()


init_api(app)
