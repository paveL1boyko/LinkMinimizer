import secrets
import string

from pydantic import BaseModel, Field


class ShortURLEntity(BaseModel):
    long_url: str
    short_code: str | None = Field(None)
    click_count: int = 0

    @classmethod
    def generate_short_url(cls) -> str:
        """Generate a cryptographically secure random short URL with 5 characters."""
        characters = string.ascii_letters + string.digits
        return "".join(secrets.choice(characters) for _ in range(5))
