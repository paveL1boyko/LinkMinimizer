import pytest
import pytest_asyncio
from app.adapters.cache.redis_cache import init_redis_cache
from app.adapters.db.mongo_db.short_url_repository import MotorMongoShortURLRepository
from app.core.config import Config
from app.use_cases.short_url_use_case import ShortURLUseCase
from motor.motor_asyncio import AsyncIOMotorClient


@pytest_asyncio.fixture
async def mongo_collection():
    """
    Async pytest fixture to provide a MongoDB collection for testing.
    This fixture initializes a connection to the MongoDB, yields the database,
    and then drops all collections in the database after the test is completed.
    """

    init_redis_cache()

    client = AsyncIOMotorClient(Config.MONGODB_DB_URL)
    db = client[Config.LINK_MINIMIZER_DB_NAME]
    collection = db.short_urls
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
    return MotorMongoShortURLRepository(collections=mongo_collection)


@pytest.fixture
def use_case(mongo_collection):
    """
    Pytest fixture to create an instance of ShortURLUseCase with a repository
    initialized with the test MongoDB collection.
    """
    repo = MotorMongoShortURLRepository(collections=mongo_collection)
    return ShortURLUseCase(repo=repo)
