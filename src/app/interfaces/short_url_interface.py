from abc import ABC, abstractmethod

from app.entities.short_url.short_url_dto import ShortURLDTO


class ShortURLRepository(ABC):
    @abstractmethod
    async def create(self, url: ShortURLDTO) -> ShortURLDTO:
        ...

    @abstractmethod
    async def get_by_short_code(self, *, short_code: str) -> ShortURLDTO | None:
        ...

    @abstractmethod
    async def update_click_count(self, short_code: str) -> None:
        ...
