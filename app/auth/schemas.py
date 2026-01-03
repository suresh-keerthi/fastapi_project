from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime   

class UserCreate(BaseModel):
    username: str
    firstname: str
    lastname: str
    email: EmailStr
    password : str = Field(min_length=8, max_length= 30)

class UserRead(BaseModel):
    uid: UUID
    username: str
    firstname: str 
    lastname: str
    email: EmailStr
    created_at : datetime
    updated_at : datetime | None

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)