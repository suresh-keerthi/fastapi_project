from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select 
from alchemy_models_test import User
import asyncio


engine = create_async_engine("postgresql+asyncpg://postgres:1729@localhost:5432/newdb")
AsyncSessionLocal = sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit = False
)

# AsyncSessionLocal class  gives us new sessions

session = AsyncSessionLocal()

async def main():
    try:
        # user = User(username="neo", firstname="Neo", lastname="Anderson",
                    # email="neo@matrix.com", hashed_password="hash")

        # session.add(user)

        # await session.commit()      # write to DB
        # await session.refresh(user) # get DB-generated fields
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()
        for user in users:
            print(user.username)

        return "suresh"

    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()  # ⚠️ VERY IMPORTANT


# ------------------------------------------------------------------------
"""
SQLALCHEMY ASYNC ORM + PYTHON CONTEXT MANAGER — MASTER CHEAT SHEET
==================================================================

This file explains:

DATABASE SIDE
• Engine
• Connection Pool
• Session
• sessionmaker
• ORM Models
• Identity Map
• Transactions
• SELECT / INSERT / UPDATE / DELETE

PYTHON SIDE
• What `async with` does internally
• __aenter__ and __aexit__
• Why sessions don't leak
"""

import asyncio
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, select, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


# ============================================================
# 1️⃣ ENGINE — DATABASE GATEWAY
# ============================================================
"""
Engine = Connection Pool Manager

It:
• Knows DB URL
• Creates connections when needed
• Reuses connections (pooling)
• Does NOT run queries itself
"""

engine = create_async_engine(
    "postgresql+asyncpg://postgres:1729@localhost:5432/newdb",
    echo=True
)


# ============================================================
# 2️⃣ DECLARATIVE BASE — ORM FOUNDATION
# ============================================================
class Base(DeclarativeBase):
    pass


# ============================================================
# 3️⃣ ORM MODEL — TABLE ↔ CLASS
# ============================================================
class User(Base):
    __tablename__ = "users"

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    username: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()")
    )


# ============================================================
# 4️⃣ SESSION FACTORY
# ============================================================
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# ============================================================
# 5️⃣ HOW ASYNC CONTEXT MANAGER WORKS (PYTHON INTERNALS)
# ============================================================
"""
When you write:

    async with AsyncSessionLocal() as session:
        body

Python turns it into:

    manager = AsyncSessionLocal()
    session = await manager.__aenter__()
    try:
        body
    except Exception as e:
        await manager.__aexit__(type(e), e, e.__traceback__)
        raise
    else:
        await manager.__aexit__(None, None, None)

So:

__aenter__ → SETUP
__aexit__  → CLEANUP (always runs)
"""


class DemoContext:
    async def __aenter__(self):
        print("Entering context (__aenter__)")
        return "resource"

    async def __aexit__(self, exc_type, exc, tb):
        print("Exiting context (__aexit__)")
        if exc:
            print("Exception detected:", exc)


# ============================================================
# 6️⃣ MAIN PROGRAM — ORM IN ACTION
# ============================================================

async def main():
    print("\n=== Python async context manager demo ===")
    async with DemoContext() as r:
        print("Using:", r)

    print("\n=== SQLAlchemy ORM demo ===")

    # Session context manager guarantees:
    # • session.close()
    # • connection returned to pool
    async with AsyncSessionLocal() as session:

        # ------------------ INSERT ------------------
        print("\n--- INSERT ---")
        new_user = User(username="neo")
        session.add(new_user)

        # COMMIT = flush changes + end transaction
        await session.commit()
        await session.refresh(new_user)
        print("Inserted user ID:", new_user.uid)

        # ------------------ SELECT ------------------
        print("\n--- SELECT ---")
        result = await session.execute(select(User))
        users = result.scalars().all()

        for user in users:
            print("User:", user.username)

        # Identity Map: same object reused
        user1 = users[0]
        user2 = await session.get(User, user1.uid)
        print("Same object in memory:", user1 is user2)

        # ------------------ UPDATE ------------------
        print("\n--- UPDATE ---")
        user1.username = "thomas"
        await session.commit()

        # ------------------ DELETE ------------------
        print("\n--- DELETE ---")
        await session.delete(user1)
        await session.commit()

        # ------------------ TRANSACTION SAFETY ------------------
        print("\n--- TRANSACTION DEMO ---")
        try:
            async with session.begin():
                bad_user = User(username="fail_user")
                session.add(bad_user)
                raise Exception("Something broke!")

        except Exception:
            print("Transaction rolled back automatically!")


# ============================================================
# PROGRAM START
# ============================================================

asyncio.run(main())


# -----------------------------------------------------------------------
"""
SQLALCHEMY SYNC ORM + PYTHON CONTEXT MANAGER — MASTER CHEAT SHEET
=================================================================

This file explains:

DATABASE SIDE
• Engine
• Connection Pool
• Session
• sessionmaker
• ORM Models
• Identity Map
• Transactions
• SELECT / INSERT / UPDATE / DELETE

PYTHON SIDE
• What `with` does internally
• __enter__ and __exit__
• Why sessions don't leak
"""

import uuid
from datetime import datetime

from sqlalchemy import create_engine, String, Boolean, DateTime, select, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


# ============================================================
# 1️⃣ ENGINE — DATABASE GATEWAY
# ============================================================
"""
Engine = Connection Pool Manager

It:
• Knows DB URL
• Creates DB connections
• Reuses them (pooling)
• Does NOT run queries itself
"""

engine = create_engine(
    "postgresql+psycopg2://postgres:1729@localhost:5432/newdb",
    echo=True
)


# ============================================================
# 2️⃣ DECLARATIVE BASE — ORM FOUNDATION
# ============================================================
class Base(DeclarativeBase):
    pass


# ============================================================
# 3️⃣ ORM MODEL — TABLE ↔ CLASS
# ============================================================
class User(Base):
    __tablename__ = "users"

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    username: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()")
    )


# ============================================================
# 4️⃣ SESSION FACTORY
# ============================================================
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


# ============================================================
# 5️⃣ HOW `with` CONTEXT MANAGER WORKS (PYTHON INTERNALS)
# ============================================================
"""
When you write:

    with SessionLocal() as session:
        body

Python turns it into:

    manager = SessionLocal()
    session = manager.__enter__()
    try:
        body
    except Exception as e:
        manager.__exit__(type(e), e, e.__traceback__)
        raise
    else:
        manager.__exit__(None, None, None)

__enter__ → SETUP
__exit__  → CLEANUP (always runs)
"""


class DemoContext:
    def __enter__(self):
        print("Entering context (__enter__)")
        return "resource"

    def __exit__(self, exc_type, exc, tb):
        print("Exiting context (__exit__)")
        if exc:
            print("Exception detected:", exc)


# ============================================================
# 6️⃣ MAIN PROGRAM — ORM IN ACTION
# ============================================================

def main():
    print("\n=== Python context manager demo ===")
    with DemoContext() as r:
        print("Using:", r)

    print("\n=== SQLAlchemy ORM demo ===")

    # Session context manager guarantees cleanup
    with SessionLocal() as session:

        # ------------------ INSERT ------------------
        print("\n--- INSERT ---")
        new_user = User(username="neo")
        session.add(new_user)

        # COMMIT = flush changes + end transaction
        session.commit()
        session.refresh(new_user)
        print("Inserted user ID:", new_user.uid)

        # ------------------ SELECT ------------------
        print("\n--- SELECT ---")
        result = session.execute(select(User))
        users = result.scalars().all()

        for user in users:
            print("User:", user.username)

        # Identity Map: same object reused
        user1 = users[0]
        user2 = session.get(User, user1.uid)
        print("Same object in memory:", user1 is user2)

        # ------------------ UPDATE ------------------
        print("\n--- UPDATE ---")
        user1.username = "thomas"
        session.commit()

        # ------------------ DELETE ------------------
        print("\n--- DELETE ---")
        session.delete(user1)
        session.commit()

        # ------------------ TRANSACTION SAFETY ------------------
        print("\n--- TRANSACTION DEMO ---")
        try:
            with session.begin():
                bad_user = User(username="fail_user")
                session.add(bad_user)
                raise Exception("Something broke!")
        except Exception:
            print("Transaction rolled back automatically!")


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()
