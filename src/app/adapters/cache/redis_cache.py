from app.core.config import Config
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette.requests import Request
from starlette.responses import Response


def init_redis_cache():
    redis = aioredis.from_url(
        Config.REDIS_CACHE_URL, encoding="utf8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


def my_key_builder(
    func,
    namespace: str = "",
    request: Request | None = None,
    response: Response | None = None,
    # *args,
    **kwargs,
):
    kwargs = kwargs.get("kwargs")
    return FastAPICache.get_key_builder()(func, namespace, kwargs=kwargs)


async def delete_cache_key(func, namespace, **kwargs):
    key = my_key_builder(func, namespace, kwargs=kwargs)
    await FastAPICache.get_backend().clear(key=key)
