from unittest.mock import patch

import pytest
from app.core.errors import DuplicateEntityError
from app.entities.short_url.short_url_entity import ShortURLEntity
from use_cases.test_factory_entity_short_url import ShortURLEntityFactory


@pytest.mark.asyncio
async def test_create_short_url_success(short_url_use_case):
    """
    Test for successful creation of a short URL.
    """
    url_entity = ShortURLEntityFactory.build()
    result = await short_url_use_case.create(url_entity)
    assert result == url_entity


@pytest.mark.asyncio
async def test_create_short_url_duplicate_error(short_url_use_case):
    """
    Test behavior when trying to create a short URL that already exists.
    Expecting a DuplicateEntityError to be raised.
    """
    url_entity = ShortURLEntityFactory.build()
    # Mock the create method of the repository to raise DuplicateEntityError
    with patch.object(
        short_url_use_case.repo, "create", side_effect=DuplicateEntityError
    ):
        with pytest.raises(DuplicateEntityError):
            await short_url_use_case.create(url_entity)


@pytest.mark.asyncio
async def test_get_by_short_code_success(short_url_use_case):
    """
    Test for successful retrieval of a short URL by its code.
    """
    url_entity: ShortURLEntity = ShortURLEntityFactory.build()
    await short_url_use_case.create(url_entity)
    result = await short_url_use_case.get_by_short_code(
        short_code=url_entity.short_code
    )
    assert result == url_entity


@pytest.mark.asyncio
async def test_get_by_short_code_not_found(short_url_use_case):
    """
    Test behavior when trying to retrieve a short URL by a non-existent code.
    Expecting the result to be None.
    """
    url_entity: ShortURLEntity = ShortURLEntityFactory.build()
    await short_url_use_case.create(url_entity)
    result = await short_url_use_case.get_by_short_code(
        short_code=url_entity.short_code + "wrong"
    )
    assert result is None


@pytest.mark.asyncio
async def test_update_click_count(short_url_use_case):
    """
    Test for updating the click count for a short URL.
    """
    url_entity: ShortURLEntity = ShortURLEntityFactory.build()
    before_update = await short_url_use_case.create(url_entity)

    await short_url_use_case.update_click_count(url_entity.short_code)
    after_update = await short_url_use_case.get_by_short_code(
        short_code=url_entity.short_code
    )
    assert before_update.click_count + 1 == after_update.click_count
