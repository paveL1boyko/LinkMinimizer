import logging
from asyncio import new_event_loop

import pytest
import pytest_asyncio
from app.adapters.cache.redis_cache import init_redis_cache
from app.adapters.db.mongo_db import (
    get_short_link_collection,
    mongo_client,
    short_url_db,
)
from app.adapters.db.mongo_db.short_url_repository import MotorMongoShortURLRepository
from app.use_cases.short_url_use_case import ShortURLUseCase
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

logging.basicConfig(level=logging.INFO)


@pytest.fixture(scope="session", autouse=True)
def redis_cache() -> None:
    """Initialize Redis cache."""
    logging.info("Initializing Redis cache...")
    init_redis_cache()


@pytest.fixture(scope="session")
def mongo_client_fixture() -> AsyncIOMotorClient:
    """Initialize and yield MongoDB client."""
    logging.info("Initializing MongoDB client...")
    client = mongo_client()
    yield client
    logging.info("Closing MongoDB client...")
    client.close()


@pytest.fixture(scope="session")
def mongo_db(mongo_client_fixture) -> AsyncIOMotorDatabase:
    """Initialize and yield MongoDB database."""
    logging.info("Initializing MongoDB database...")
    yield short_url_db(client=mongo_client_fixture)


@pytest_asyncio.fixture(scope="session")
async def mongo_collection(mongo_db) -> AsyncIOMotorCollection:
    """Initialize and yield MongoDB collection."""
    logging.info("Initializing MongoDB collection...")
    collection = await get_short_link_collection(db=mongo_db)
    yield collection


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_mongo_collection(mongo_collection) -> None:
    """Automatically clean up MongoDB collection after each test."""
    yield
    logging.info("Cleaning up MongoDB collection...")
    await mongo_collection.delete_many({})


@pytest.fixture
def short_url_repository_fixture(mongo_collection) -> MotorMongoShortURLRepository:
    """Initialize and yield Short URL repository."""
    logging.info("Initializing Short URL repository...")
    return MotorMongoShortURLRepository(collection=mongo_collection)


@pytest.fixture
def short_url_use_case_fixture(short_url_repository_fixture) -> ShortURLUseCase:
    """Initialize and yield Short URL use case."""
    logging.info("Initializing Short URL use case...")
    return ShortURLUseCase(repo=short_url_repository_fixture)


@pytest.fixture(scope="session")
def event_loop() -> None:
    """Initialize and yield new asyncio event loop."""
    logging.info("Initializing asyncio event loop...")
    loop = new_event_loop()
    yield loop
    logging.info("Closing asyncio event loop...")
    loop.close()
