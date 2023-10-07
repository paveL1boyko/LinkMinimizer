import secrets
import string

from pydantic import BaseModel, Field


class ShortURLEntity(BaseModel):
    """
    Entity for representing Short URLs.
    """

    long_url: str = Field(..., description="The original long URL.")
    short_code: str | None = Field(
        None, description="The generated short code for the URL."
    )
    click_count: int = Field(
        0, description="The number of times the short URL has been clicked."
    )

    @classmethod
    def generate_short_url(cls) -> str:
        """
        Generate a cryptographically secure random short URL with 5 characters.

        :return: The randomly generated short URL code.
        """
        characters = string.ascii_letters + string.digits
        return "".join(secrets.choice(characters) for _ in range(5))
