import logging

from app.core.config import Config
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)


async def init_short_url_db() -> tuple[
    AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
]:
    """
    Initialize the MongoDB database connection and create an index for short_code.

    :return: A tuple containing the database and short_link_collection.
    """
    logging.info("Connecting to MongoDB...")
    client = AsyncIOMotorClient(Config.MONGODB_DB_URL)

    db = client[Config.LINK_MINIMIZER_DB_NAME]
    short_link_collection = db.short_urls

    await short_link_collection.create_index("short_code", unique=True)
    logging.info("Index for short_code created successfully.")

    return client, db, short_link_collection
