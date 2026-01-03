from sqlmodel import SQLModel, Field, Column
from sqlalchemy import text
from sqlalchemy.dialects import postgresql as pg
from uuid import UUID
from datetime import datetime, date


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: UUID = Field(
        primary_key=True,
        index=True,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()")
        }
    )

    title: str
    author: str
    publisher: str
    page_count: int
    language: str
    published_date: date
    created_at: datetime = Field(
        sa_column_kwargs={
            "server_default": text("NOW()")
        }
    )
    updated_at: datetime | None = Field(default=None)




class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: UUID = Field(
        primary_key=True,
        index=True,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
        }
    )

    username: str
    firstname: str
    lastname: str
    email: str
    hashed_password: str = Field(nullable= False)
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(
        sa_column_kwargs={
            "server_default": text("NOW()")
        }
    )
    
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    updated_at: datetime | None = Field(default=None)