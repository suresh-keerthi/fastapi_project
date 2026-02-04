from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class ReviewCreate(BaseModel):
    review_text : str
    rating : float  = Field(ge = 0, le = 5)

class ReviewRead(ReviewCreate):
    uid : UUID
    book_uid : UUID
    user_uid : UUID
    created_at : datetime
    updated_at : datetime | None = None

class ReviewUpdate(BaseModel):
    review_text : str | None = None
    rating : float | None = Field(default=None, ge = 0, le = 5)

