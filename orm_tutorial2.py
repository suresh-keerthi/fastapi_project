"""
==============================================================
   ASYNC SQLALCHEMY + SQLMODEL + FASTAPI DEPENDENCY BIBLE
==============================================================

This file demonstrates:

DATABASE SIDE
• Engine
• Connection Pool
• AsyncSession
• sessionmaker
• ORM Relationships
• Identity Map
• Transactions

PYTHON SIDE
• async with internals
• async generators
• __anext__(), aclose()
• How FastAPI handles dependencies

COMMON MISTAKES INCLUDED + EXPLAINED
"""

# ============================================================
# 1️⃣ IMPORTS
# ============================================================

import asyncio
import uuid
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from sqlmodel import SQLModel, Field, Relationship


# ============================================================
# 2️⃣ ENGINE (Connection Pool Manager)
# ============================================================

engine = create_async_engine(
    "postgresql+asyncpg://postgres:1729@localhost:5432/newdb",
    echo=True
)

"""
Engine owns the connection pool.
Sessions borrow connections from this pool.
"""


# ============================================================
# 3️⃣ MODELS (SQLModel ORM Relationships)
# ============================================================

class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    username: str
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("NOW()")})

    books: List["Book"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},  # avoids N+1
    )

    reviews: List["Review"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")

    title: str
    published_date: date

    user: Optional[User] = Relationship(
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    reviews: List["Review"] = Relationship(
        back_populates="book",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )

    book_uid: uuid.UUID = Field(foreign_key="books.uid")
    user_uid: uuid.UUID = Field(foreign_key="users.uid")

    review_text: str
    rating: int = Field(ge=1, le=5)

    book: Book = Relationship(back_populates="reviews")
    user: User = Relationship(back_populates="reviews")


# ============================================================
# 4️⃣ SESSION FACTORY
# ============================================================

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# ============================================================
# 5️⃣ FASTAPI-STYLE DEPENDENCY (ASYNC GENERATOR)
# ============================================================

async def get_session():
    """
    This is NOT a normal function.
    It is an ASYNC GENERATOR.

    Python automatically gives it:
    • __anext__()
    • asend()
    • athrow()
    • aclose()
    """
    async with AsyncSessionLocal() as session:
        yield session  # pause point


# ============================================================
# 6️⃣ HOW FASTAPI DRIVES DEPENDENCY (INTERNALS)
# ============================================================

"""
FastAPI basically does this:

agen = get_session()
session = await agen.__anext__()

try:
    # your route runs
finally:
    await agen.aclose()
"""


# ============================================================
# 7️⃣ USING DEPENDENCY OUTSIDE FASTAPI (CORRECT)
# ============================================================

async def use_dependency_correctly():
    async for session in get_session():  # safest way
        result = await session.execute(select(User))
        print("Users:", result.scalars().all())


# ============================================================
# 8️⃣ ADVANCED MANUAL CONTROL
# ============================================================

async def manual_generator_control():
    agen = get_session()
    session = await agen.__anext__()

    try:
        user = User(username="neo")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print("Inserted:", user.uid)
    finally:
        await agen.aclose()  # must close


# ============================================================
# 9️⃣ COMMON MISTAKES
# ============================================================

"""
❌ session = get_session()
   → generator, not session

❌ session = get_session().__anext__()
   → coroutine, not session

❌ calling __anext__ twice
   → opens new session, leaks old

❌ mixing sync Session with await

❌ forgetting aclose()
"""


# ============================================================
# 🔟 CONTEXT MANAGER VS GENERATOR
# ============================================================

"""
async with X():
    calls __aenter__ / __aexit__

async def gen(): yield
    controlled by __anext__ / aclose

FastAPI dependency = BOTH
"""


# ============================================================
# 1️⃣1️⃣ MAIN DEMO
# ============================================================

async def main():
    print("\n--- Correct dependency usage ---")
    await use_dependency_correctly()

    print("\n--- Manual generator control ---")
    await manual_generator_control()


asyncio.run(main())

"""
==============================================================
FINAL MENTAL MODEL
==============================================================

Engine → Pool → Connection
Session → borrows connection
Dependency → wraps session in async generator
FastAPI → drives generator lifecycle
Python → provides aclose/anext machinery

Understanding this = Senior backend ORM knowledge
"""
