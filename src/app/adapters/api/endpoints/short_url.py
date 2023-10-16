import logging

from app.adapters.cache.redis_cache import delete_cache_key
from app.adapters.db.mongo_db import get_short_link_collection
from app.adapters.db.mongo_db.short_url_repository import MotorMongoShortURLRepository
from app.core.config import Config
from app.core.errors import DuplicateEntityError
from app.entities.short_url.short_url_entity import ShortURLEntity
from app.frameworks_and_drivers.api_models import (
    ClickCountResponse,
    ShortURLResponse,
    URLPayload,
)
from app.use_cases.short_url_use_case import ShortURLUseCase
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_cache.decorator import cache
from motor.motor_asyncio import AsyncIOMotorCollection

from .error_messages import ERROR_SHORT_CODE_CONFLICT, ERROR_SHORT_URL_NOT_FOUND

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/short_url")


def get_use_case(
    short_link_collection: AsyncIOMotorCollection = Depends(get_short_link_collection),
) -> ShortURLUseCase:
    return ShortURLUseCase(
        MotorMongoShortURLRepository(collection=short_link_collection)
    )


@router.post(
    "/generate_short_url/",
    response_model=ShortURLResponse,
    responses={409: {"description": ERROR_SHORT_CODE_CONFLICT}},
)
async def create_short_url(
    payload: URLPayload, repo: ShortURLUseCase = Depends(get_use_case)
):
    """Generate and store a short URL for the given long URL."""
    try:
        logger.info(f"Generating short URL for {payload.long_url}")
        return await repo.create(ShortURLEntity(**payload.model_dump()))
    except DuplicateEntityError:
        logging.error("Short code conflict. Unable to generate a unique short code.")
        raise HTTPException(
            status_code=409,
            detail="Short code conflict. Unable to generate a unique short code.",
        )


@router.get(
    "/get_long_url/{short_code}",
    response_model=ShortURLResponse,
    responses={404: {"description": ERROR_SHORT_URL_NOT_FOUND}},
)
@cache(expire=Config.CACHE_TIME)
async def get_long_url(
    short_code: str, use_case: ShortURLUseCase = Depends(get_use_case)
):
    """Retrieve the original URL for the given short code."""
    short_url_data = await use_case.get_by_short_code(short_code=short_code)
    if not short_url_data:
        logger.error(f"Short URL not found for code {short_code}")
        raise HTTPException(status_code=404, detail=ERROR_SHORT_URL_NOT_FOUND)
    return short_url_data


@router.get(
    "/{short_code}", responses={404: {"description": ERROR_SHORT_URL_NOT_FOUND}}
)
async def redirect_to_long_url(
    short_code: str, use_case: ShortURLUseCase = Depends(get_use_case)
):
    """Redirect to the original long URL using the short code."""
    url = await use_case.get_by_short_code(short_code=short_code)
    await delete_cache_key(
        use_case.get_by_short_code,
        namespace=use_case.cache_namespace,
        short_code=short_code,
    )
    if not url:
        logger.error(f"Short URL not found for code {short_code}")
        raise HTTPException(status_code=404, detail=ERROR_SHORT_URL_NOT_FOUND)
    await use_case.update_click_count(short_code)
    return RedirectResponse(url=f"/get_long_url/{short_code}")


@router.get(
    "/count/{short_code}",
    response_model=ClickCountResponse,
    responses={404: {"description": ERROR_SHORT_URL_NOT_FOUND}},
)
async def get_click_count(
    short_code: str, use_case: ShortURLUseCase = Depends(get_use_case)
):
    """Retrieve the click count for the given short code."""
    url = await use_case.get_by_short_code(short_code=short_code)
    if not url:
        logger.error(f"Short URL not found for code {short_code}")
        raise HTTPException(status_code=404, detail=ERROR_SHORT_URL_NOT_FOUND)
    return ClickCountResponse(**(url if isinstance(url, dict) else url.model_dump()))
