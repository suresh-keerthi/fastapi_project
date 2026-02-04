from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str

class TagRead(TagCreate):
    uid: str
    created_at: str
    updated_at: str | None = None

class BookTagLinkRead(BaseModel):
    book_uid: str
    tag_uid: str