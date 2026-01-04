from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID


class BookCreate(BaseModel):
    title: str
    author: str
    publisher : str
    page_count: int
    language: str
    published_date: date

class BookRead(BookCreate):
    uid : UUID
    updated_at : datetime | None = None
    created_at : datetime
    user_uid : UUID | None = None

class BookUpdate(BaseModel):
    title: str  | None = None
    author: str | None = None
    publisher : str |None  = None 
    page_count: int | None = None
    language: str | None = None
    published_date: date | None = None
