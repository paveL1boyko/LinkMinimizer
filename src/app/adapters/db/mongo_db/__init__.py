import logging

from app.core.config import Config
from fastapi import Depends
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

logging.basicConfig(level=logging.INFO)


def mongo_client(mongo_url: str = Config.MONGODB_DB_URL) -> AsyncIOMotorClient:
    """
    Initialize and return MongoDB client.

    :param mongo_url: MongoDB connection URL
    :return: MongoDB client
    """
    logging.info(f"Connecting to MongoDB at {mongo_url}...")
    return AsyncIOMotorClient(mongo_url)


def short_url_db(
    client: AsyncIOMotorClient = Depends(mongo_client),
    db_name: str = Config.LINK_MINIMIZER_DB_NAME,
) -> AsyncIOMotorDatabase:
    """
    Get MongoDB database from a client.

    :param client: MongoDB client
    :param db_name: Database name
    :return: MongoDB Database
    """
    logging.info(f"Accessing database {db_name}")
    return client[db_name]


async def get_short_link_collection(
    db: AsyncIOMotorDatabase = Depends(short_url_db),
) -> AsyncIOMotorCollection:
    """
    Initialize the MongoDB database connection and create an index for short_code.

    :param db: MongoDB Database
    :return: MongoDB Collection for short links
    """
    collection = db.short_urls
    await collection.create_index("short_code", unique=True)
    logging.info("Index for short_code created successfully.")
    return collection
