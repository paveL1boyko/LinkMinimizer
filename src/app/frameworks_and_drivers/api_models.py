from pydantic import BaseModel


class URLPayload(BaseModel):
    long_url: str


class ShortURLResponse(BaseModel):
    short_code: str
    long_url: str


class ClickCountResponse(BaseModel):
    click_count: int
