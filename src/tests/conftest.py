import pytest
import pytest_asyncio
from app.adapters.cache.redis_cache import init_redis_cache
from app.adapters.db.mongo_db import init_short_url_db
from app.adapters.db.mongo_db.short_url_repository import MotorMongoShortURLRepository
from app.use_cases.short_url_use_case import ShortURLUseCase


@pytest.fixture(scope="session")
def event_loop():
    from asyncio import new_event_loop

    loop = new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def mongo_client(event_loop):
    init_redis_cache()
    client, db, short_link_collection = await init_short_url_db()
    yield client, db, short_link_collection
    client.close()


@pytest_asyncio.fixture(scope="function")
async def mongo_collection(mongo_client):
    client, db, short_link_collection = mongo_client
    yield short_link_collection
    collections = await db.list_collection_names()
    for collection in collections:
        await db.drop_collection(collection)


@pytest.fixture
def short_url_repository(mongo_collection):
    """
    Pytest fixture to provide an instance of the MotorMongoShortURLRepository.
    This repository is initialized with the provided mongo_collection.
    """
    return MotorMongoShortURLRepository(collection=mongo_collection)


@pytest.fixture
def short_url_use_case(short_url_repository):
    """
    Pytest fixture to create an instance of ShortURLUseCase with a repository
    initialized with the test MongoDB collection.
    """
    return ShortURLUseCase(repo=short_url_repository)
