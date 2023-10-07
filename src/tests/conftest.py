import pytest
import pytest_asyncio
from app.adapters.cache.redis_cache import init_redis_cache
from app.adapters.db.mongo_db import init_short_url_db
from app.adapters.db.mongo_db.short_url_repository import MotorMongoShortURLRepository
from app.use_cases.short_url_use_case import ShortURLUseCase


@pytest_asyncio.fixture
async def mongo_collection():
    """
    Async pytest fixture to provide a MongoDB collection for testing.
    This fixture initializes a connection to the MongoDB, yields the database,
    and then drops all collections in the database after the test is completed.
    """

    init_redis_cache()

    client, db, collection = await init_short_url_db()
    yield collection

    collections = await db.list_collection_names()
    for collection in collections:
        await db.drop_collection(collection)
    client.close()


@pytest.fixture
def short_url_repository(mongo_collection):
    """
    Pytest fixture to provide an instance of the MotorMongoShortURLRepository.
    This repository is initialized with the provided mongo_collection.
    """
    return MotorMongoShortURLRepository(collection=mongo_collection)


@pytest.fixture
def use_case(mongo_collection):
    """
    Pytest fixture to create an instance of ShortURLUseCase with a repository
    initialized with the test MongoDB collection.
    """
    repo = MotorMongoShortURLRepository(collection=mongo_collection)
    return ShortURLUseCase(repo=repo)
