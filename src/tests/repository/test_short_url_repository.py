import pytest
from app.entities.short_url.short_url_dto import ShortURLDTO
from repository.test_factory_dto_short_url import ShortURLDTOFactory


@pytest.mark.asyncio
async def test_create_short_url(short_url_repository):
    """
    Test the creation of a short URL in the repository.
    This test ensures that a short URL can be created and then retrieved
    from the repository with the expected data.
    """
    data: ShortURLDTO = ShortURLDTOFactory.build()
    result = await short_url_repository.create(data)
    response_from_db = await short_url_repository.get_by_short_code(
        short_code=data.short_code
    )
    assert result.model_dump() == response_from_db.model_dump()


@pytest.mark.asyncio
async def test_get_by_short_code(short_url_repository):
    """
    Test the retrieval of a short URL by its short code from the repository.
    This test ensures that the correct short URL is retrieved when multiple
    short URLs exist in the repository.
    """
    data: ShortURLDTO = ShortURLDTOFactory.build()
    await short_url_repository.create(data)
    await short_url_repository.create(ShortURLDTOFactory.build())

    result = await short_url_repository.get_by_short_code(short_code=data.short_code)

    assert result.model_dump() == data.model_dump()


@pytest.mark.asyncio
async def test_update_click_count(short_url_repository):
    """
    Test the update of the click count for a short URL in the repository.
    This test ensures that the click count for a short URL can be incremented
    and then retrieved with the updated count.
    """
    data: ShortURLDTO = ShortURLDTOFactory.build()
    result = await short_url_repository.create(data)
    assert result.click_count == data.click_count
    result_after_update = await short_url_repository.update_click_count(data.short_code)
    assert (data.click_count + 1) == result_after_update.click_count
