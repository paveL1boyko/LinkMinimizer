from pydantic import BaseModel, Field


class URLPayload(BaseModel):
    """
    A Pydantic model for the payload containing a long URL.
    """

    long_url: str = Field(..., description="The original long URL to be shortened.")


class ShortURLResponse(BaseModel):
    """
    A Pydantic model for the response containing the short URL code and the original long URL.
    """

    short_code: str = Field(..., description="The shortened URL code.")
    long_url: str = Field(..., description="The original long URL.")


class ClickCountResponse(BaseModel):
    """
    A Pydantic model for the response containing the click count for a short URL.
    """

    click_count: int = Field(
        ..., description="The number of times the short URL has been clicked."
    )
