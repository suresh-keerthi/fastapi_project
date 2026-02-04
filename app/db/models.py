from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text
from uuid import UUID
from datetime import datetime, date
from typing import List, Optional


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: UUID = Field(
        primary_key=True,
        index=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    username: str
    firstname: str
    lastname: str
    email: str
    hashed_password: str = Field(nullable=False)
    is_active: bool = True
    is_verified: bool = False
    role: str = Field(
        nullable=False, sa_column_kwargs={"server_default": text("'user'")}
    )
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("NOW()")})
    updated_at: Optional[datetime] = None
    books: List["Book"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    reviews: List["Review"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self):
        return f"<user {self.username}>" 

class Book(SQLModel, table=True):
    __tablename__ = "books"
    uid: UUID = Field(
        primary_key=True,
        index=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    user_uid: Optional[UUID] = Field(default=None, foreign_key="users.uid")
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
    published_date: date
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("NOW()")})
    updated_at: Optional[datetime] = None
    user: Optional[User] = Relationship(
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    reviews: List["Review"] = Relationship(
        back_populates="book",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self):
        return f"<Book {self.title}"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: UUID = Field(
        primary_key=True,
        index=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    book_uid: UUID = Field(foreign_key="books.uid")
    user_uid: UUID = Field(foreign_key="users.uid")
    review_text: str
    rating: float = Field(ge=0, le=5)
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("NOW()")})
    updated_at: Optional[datetime] = None
    book: Book = Relationship(
        back_populates="reviews",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    user: User = Relationship(
        back_populates="reviews",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self):
        return "f<review by {self.user.username}({self.user_uid}) on book {self.book.title}({self.book_uid})>"
