import logging

from app.core.errors import DuplicateEntityError, NotFoundError
from app.entities.short_url.short_url_dto import ShortURLDTO
from app.interfaces.short_url_interface import ShortURLRepository
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument

logger = logging.getLogger(__name__)


class MotorMongoShortURLRepository(ShortURLRepository):
    """
    MongoDB repository for ShortURL operations using the Motor asynchronous driver.
    """

    def __init__(self, collection: AsyncIOMotorCollection):
        """
        Initialize the repository with the given database collection.

        :param collection: The Motor asynchronous collection to use for short URL operations.
        """
        self.collection = collection

    async def create(self, url: ShortURLDTO) -> ShortURLDTO:
        """
        Create a new short URL record in the database.

        :param url: The short URL data transfer object.
        :return: The created short URL with its ID.
        :raises DuplicateEntityError: If a short URL with the same code already exists.
        """
        existed_long_url = await self.collection.find_one({"long_url": url.long_url})
        if existed_long_url:
            logger.warning(f"Short URL with long URL '{url.long_url}' already exists.")
            return ShortURLDTO(**existed_long_url)
        else:
            try:
                result = await self.collection.insert_one(
                    url.model_dump(exclude_none=True)
                )
                url.id = str(result.inserted_id)
                logger.info(f"Short URL created with ID {url.id}.")
            except Exception as e:
                logger.error(f"Error creating short URL: {str(e)}")
                raise DuplicateEntityError(
                    f"Short URL with code {url.short_code} already exists."
                ) from e
            return url

    async def get_by_short_code(self, short_code: str) -> ShortURLDTO | None:
        """
        Retrieve a short URL from the database by its short code.

        :param short_code: The short code of the URL.
        :return: The short URL data transfer object if found, else None.
        """
        doc = await self.collection.find_one({"short_code": short_code})
        if doc:
            logger.info(f"Retrieved short URL with code {short_code}.")
            return ShortURLDTO(**doc)
        else:
            logger.warning(f"Short URL with code {short_code} not found.")
            return None

    async def update_click_count(self, short_code: str) -> ShortURLDTO:
        """
        Update the click count of a short URL in the database.

        :param short_code: The short code of the URL.
        :return: The updated short URL data transfer object.
        :raises NotFoundError: If the short URL with the given code is not found.
        """
        result = await self.collection.find_one_and_update(
            {"short_code": short_code},
            {"$inc": {"click_count": 1}},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            logger.warning(f"Short URL with code {short_code} not found.")
            raise NotFoundError(f"Short URL with code {short_code} not found.")
        else:
            logger.info(f"Updated click count for short URL with code {short_code}.")
            return ShortURLDTO(**result)
