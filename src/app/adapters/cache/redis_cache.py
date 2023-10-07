import logging

from app.core.config import Config
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


def init_redis_cache():
    """
    Initialize the Redis cache for FastAPI.
    """
    logger.info("Initializing Redis cache...")
    redis = aioredis.from_url(
        Config.REDIS_CACHE_URL, encoding="utf8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    logger.info("Redis cache initialized.")


def my_key_builder(
    func,
    namespace: str = "",
    request: Request | None = None,
    response: Response | None = None,
    **kwargs,
) -> str:
    """
    Custom key builder for FastAPI cache.

    :param func: The function for which the cache key is being built.
    :param namespace: Optional namespace for the cache key.
    :param request: Optional FastAPI request object.
    :param response: Optional FastAPI response object.
    :param kwargs: Additional keyword arguments.
    :return: The cache key as a string.
    """
    kwargs = kwargs.get("kwargs")
    return FastAPICache.get_key_builder()(func, namespace, kwargs=kwargs)


async def delete_cache_key(func, namespace: str, **kwargs):
    """
    Delete a specific cache key.

    :param func: The function for which the cache key is being deleted.
    :param namespace: The namespace for the cache key.
    :param kwargs: Additional keyword arguments.
    """
    logger.info(
        f"Deleting cache key for function {func.__name__} in namespace {namespace}"
    )
    key: str = my_key_builder(func, namespace, kwargs=kwargs)
    await FastAPICache.get_backend().clear(key=key)
    logger.info(f"Cache {key=} deleted.")
