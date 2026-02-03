from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime   
from app.db.models import Book
from typing import List

class UserCreate(BaseModel):
    username: str 
    firstname: str
    lastname: str
    email: EmailStr
    password : str = Field(min_length=8, max_length= 30)

class UserRead(BaseModel):
    role: str
    uid: UUID
    username: str
    firstname: str 
    lastname: str
    email: EmailStr
    created_at : datetime
    updated_at : datetime | None
    books : List[Book] | None 

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)