from app.adapters.cache.redis_cache import my_key_builder
from app.core.config import Config
from app.core.errors import DuplicateEntityError
from app.entities.short_url.short_url_dto import ShortURLDTO
from app.entities.short_url.short_url_entity import ShortURLEntity
from app.interfaces.short_url_interface import ShortURLRepository
from fastapi_cache.decorator import cache


class ShortURLUseCase:
    cache_namespace = "get_by_short_code"

    def __init__(self, repo: ShortURLRepository):
        """
        Use Case for Short URLs.

        :param repo: Repository interface for Short URLs.
        :type repo: ShortURLRepository
        """
        self.repo = repo

    async def create(self, url_entity: ShortURLEntity) -> ShortURLEntity:
        """
        Create a new short URL.

        :param url_entity: Entity containing the long URL and its corresponding short code.
        :return: The created short URL entity.
        """
        for _ in range(Config.RETRY_COUNT_TO_CREATE_UNIQUE_SHORT_CODE):
            try:
                url_entity.short_code = ShortURLEntity.generate_short_url()
                new_url = await self.repo.create(ShortURLDTO(**url_entity.model_dump()))
                return ShortURLEntity(**new_url.model_dump())
            except DuplicateEntityError:
                continue
        raise DuplicateEntityError(
            "Failed to create a unique short URL after 5 attempts."
        )

    @cache(
        expire=Config.CACHE_TIME, key_builder=my_key_builder, namespace=cache_namespace
    )
    async def get_by_short_code(self, *, short_code: str) -> ShortURLEntity | None:
        """
        Retrieve a short URL by its short code.

        :param short_code: The short code corresponding to the URL.
        :return: The retrieved short URL entity.
        """
        dto = await self.repo.get_by_short_code(short_code=short_code)
        if dto:
            return ShortURLEntity(**dto.model_dump())

    async def update_click_count(self, short_code: str) -> None:
        """
        Increment the click count of a short URL.

        :param short_code: The short code of the URL whose click count needs to be updated.
        :type short_code: str
        """
        await self.repo.update_click_count(short_code)
