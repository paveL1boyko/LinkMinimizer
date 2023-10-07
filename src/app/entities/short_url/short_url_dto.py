from bson import ObjectId
from pydantic import BaseModel, Field, field_validator


class ShortURLDTO(BaseModel):
    """
    Data transfer object (DTO) for Short URL entities.
    """

    id: str | None = Field(
        None, alias="_id", description="The unique identifier of the short URL."
    )
    long_url: str = Field(..., description="The original long URL.")
    short_code: str = Field(..., description="The shortened code for the URL.")
    click_count: int = Field(
        0, description="The number of times the short URL has been clicked."
    )

    @field_validator("id", mode="before")
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
