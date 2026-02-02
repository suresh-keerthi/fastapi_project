from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text
from sqlalchemy.dialects import postgresql as pg
from uuid import UUID
from datetime import datetime, date
from typing import List


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: UUID = Field(
        primary_key=True,
        index=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")}
    )
    
    username: str
    firstname: str
    lastname: str
    email: str
    hashed_password: str = Field(nullable=False)

    is_active: bool = True
    is_verified: bool = False

    role: str = Field(
        nullable=False,
        sa_column_kwargs={"server_default": text("'user'")}
    )

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": text("NOW()")}
    )

    updated_at: datetime | None = None

    books: List["Book"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: UUID = Field(
        primary_key=True,
        index=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")}
    )

    user_uid: UUID | None = Field(
        default=None,
        foreign_key="users.uid"
    )

    user: User | None = Relationship(
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    title: str
    author: str
    publisher: str
    page_count: int
    language: str
    published_date: date

    created_at: datetime = Field(
        sa_column_kwargs={"server_default": text("NOW()")}
    )

    updated_at: datetime | None = None
