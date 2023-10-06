from bson import ObjectId
from pydantic import BaseModel, Field, field_validator


class ShortURLDTO(BaseModel):
    id: str | None = Field(None, alias="_id")
    long_url: str
    short_code: str
    click_count: int = 0

    @field_validator("id", mode="before")
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
