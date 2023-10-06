from unittest.mock import patch

import httpx
import pytest
import pytest_asyncio
from adapters.endpoints.test_factory_api_model import URLPayloadFactory
from app.adapters.api.endpoints.error_messages import (
    ERROR_SHORT_CODE_CONFLICT,
    ERROR_SHORT_URL_NOT_FOUND,
)
from app.core.errors import DuplicateEntityError
from app.frameworks_and_drivers.api_models import (
    ClickCountResponse,
    ShortURLResponse,
    URLPayload,
)
from app.frameworks_and_drivers.asgi import app, startup_event
from fastapi_cache import FastAPICache


@pytest_asyncio.fixture
async def async_client(mongo_collection):
    await startup_event()
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client
        FastAPICache.reset()


class TestShortURL:
    """Test class for ShortURL endpoints."""

    create_short_url_name: str = "create_short_url"
    get_long_url_name: str = "get_long_url"
    redirect_name: str = "redirect_to_long_url"
    get_click_count_name: str = "get_click_count"

    @staticmethod
    def get_api_path(name: str, short_code: str | None = None) -> str:
        if short_code:
            return app.url_path_for(name, short_code=short_code)
        return app.url_path_for(name)

    @pytest.mark.asyncio
    async def test_create_short_url(self, async_client):
        """
        Test the endpoint for generating a short URL.

        This test ensures that a short URL is generated and returned
        when a valid long URL is provided.
        """
        request_data: URLPayload = URLPayloadFactory.build()
        response = await async_client.post(
            self.get_api_path(self.create_short_url_name),
            json=request_data.model_dump(),
        )
        assert response.status_code == 200
        assert ShortURLResponse(**response.json())

    @pytest.mark.asyncio
    async def test_get_long_url(self, async_client):
        """
        Test the endpoint for retrieving the original URL using a short code.

        This test first creates a short URL and then attempts to retrieve
        the original long URL using the generated short code.
        """
        request_data: URLPayload = URLPayloadFactory.build()
        response = await async_client.post(
            self.get_api_path(self.create_short_url_name),
            json=request_data.model_dump(),
        )
        response_data = ShortURLResponse(**response.json())

        response = await async_client.get(
            self.get_api_path(
                self.get_long_url_name, short_code=response_data.short_code
            )
        )
        assert response.status_code == 200
        assert ShortURLResponse(**response.json()) == response_data

    @pytest.mark.asyncio
    async def test_redirect_to_long_url(self, async_client):
        """
        Test the redirection endpoint using a short code.

        This test first creates a short URL and then uses the generated
        short code to redirect to the original long URL.
        """
        request_data: URLPayload = URLPayloadFactory.build()
        response = await async_client.post(
            self.get_api_path(self.create_short_url_name),
            json=request_data.model_dump(),
        )
        response_data = ShortURLResponse(**response.json())

        response = await async_client.get(
            self.get_api_path(self.redirect_name, short_code=response_data.short_code)
        )
        assert response.status_code == 307

    @pytest.mark.asyncio
    async def test_get_click_count(self, async_client):
        """
        Test the endpoint for retrieving the click count of a short code.

        This test first creates a short URL and then retrieves the click count
        for the generated short code, ensuring it matches the expected value.
        """
        # create new record
        request_data: URLPayload = URLPayloadFactory.build()
        response = await async_client.post(
            self.get_api_path(self.create_short_url_name),
            json=request_data.model_dump(),
        )
        # get counter
        response_data = ShortURLResponse(**response.json())
        response = await async_client.get(
            self.get_api_path(
                self.get_click_count_name, short_code=response_data.short_code
            )
        )
        assert response.status_code == 200

        # update counter
        assert ClickCountResponse(**response.json()).click_count == 0
        await async_client.get(
            self.get_api_path(self.redirect_name, short_code=response_data.short_code)
        )
        # check after update
        response_after_click = await async_client.get(
            self.get_api_path(
                self.get_click_count_name, short_code=response_data.short_code
            )
        )
        assert response.status_code == 200

        assert ClickCountResponse(**response_after_click.json()).click_count == 1

    @pytest.mark.asyncio
    async def test_get_long_url_nonexistent_code(self, async_client):
        """Test retrieving a long URL with a nonexistent short code."""
        response = await async_client.get(
            self.get_api_path(self.get_long_url_name, short_code="nonexist")
        )
        assert response.status_code == 404
        assert response.json()["detail"] == ERROR_SHORT_URL_NOT_FOUND

    @pytest.mark.asyncio
    async def test_redirect_to_long_url_nonexistent_code(self, async_client):
        """Test redirection with a nonexistent short code."""
        response = await async_client.get(
            self.get_api_path(self.redirect_name, short_code="nonexistentcode")
        )
        assert response.status_code == 404
        assert response.json()["detail"] == ERROR_SHORT_URL_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_click_count_nonexistent_code(self, async_client):
        """Test retrieving click count with a nonexistent short code."""
        response = await async_client.get(
            self.get_api_path(self.get_click_count_name, short_code="nonexistentcode")
        )
        assert response.status_code == 404
        assert response.json()["detail"] == ERROR_SHORT_URL_NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_short_url_duplicate_error(self, async_client):
        request_data: URLPayload = URLPayloadFactory.build()
        with patch(
            "app.use_cases.short_url_use_case.ShortURLUseCase.create",
            side_effect=DuplicateEntityError,
        ):
            response = await async_client.post(
                self.get_api_path(self.create_short_url_name),
                json=request_data.model_dump(),
            )
            assert response.status_code == 409
            assert response.json()["detail"] == ERROR_SHORT_CODE_CONFLICT
