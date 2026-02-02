from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Integer,
    ForeignKey,
    text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, date
import uuid


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()")
    )

    username: Mapped[str] = mapped_column(String, nullable=False)
    firstname: Mapped[str] = mapped_column(String, nullable=False)
    lastname: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    role: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'user'")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()")
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=datetime.utcnow
    )

    # # Relationship
    # books: Mapped[list["Book"]] = relationship(
    #     back_populates="user",
    #     lazy="selectin"
    # )


# class Book(Base):
#     __tablename__ = "books"

#     uid: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         index=True,
#         server_default=text("gen_random_uuid()")
#     )

#     user_uid: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.uid"),
#         nullable=True
#     )

#     user: Mapped["User" | None] = relationship(
#         back_populates="books",
#         lazy="selectin"
#     )

#     title: Mapped[str] = mapped_column(String, nullable=False)
#     author: Mapped[str] = mapped_column(String, nullable=False)
#     publisher: Mapped[str] = mapped_column(String, nullable=False)
#     page_count: Mapped[int] = mapped_column(Integer, nullable=False)
#     language: Mapped[str] = mapped_column(String, nullable=False)
#     published_date: Mapped[date] = mapped_column(nullable=False)

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         server_default=text("NOW()")
#     )

#     updated_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#         onupdate=datetime.utcnow
#     )
