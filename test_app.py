
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import config

# -------------------------------------------------------------------
# DATABASE CONFIG 
# -------------------------------------------------------------------


DATABASE_URL = config.DATABASE_URL 

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# -------------------------------------------------------------------
# MODEL 
# -------------------------------------------------------------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str = Field(unique=True, index=True)
    age: int
    password: str

# -------------------------------------------------------------------
# LIFESPAN (startup + shutdown) 
# -------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield  # app runs here

    # SHUTDOWN
    await engine.dispose()


# -------------------------------------------------------------------
# APP
# -------------------------------------------------------------------

app = FastAPI(lifespan=lifespan)

# -------------------------------------------------------------------
# SESSION DEPENDENCY
# -------------------------------------------------------------------

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# -------------------------------------------------------------------
# CREATE
# -------------------------------------------------------------------

@app.post("/users", response_model=User)
async def create_user(
    user: User,
    session: AsyncSession = Depends(get_session),
):
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# -------------------------------------------------------------------
# READ
# -------------------------------------------------------------------

@app.get("/users/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/by-username/{username}", response_model=User)
async def get_user_by_username(
    username: str,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(User).where(User.user_name == username)
    result = await session.exec(stmt)
    user = result.first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.get("/users", response_model=list[User])
async def get_all_users(
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(User))
    return result.all()


@app.get("/users/search")
async def search_users(
    min_age: int,
    max_age: int,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(User).where(
        User.age >= min_age,
        User.age <= max_age,
    )
    result = await session.exec(stmt)
    return result.all()

# -------------------------------------------------------------------
# UPDATE
# -------------------------------------------------------------------

@app.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    new_data: User,
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.user_name = new_data.user_name
    user.age = new_data.age
    user.password = new_data.password

    await session.commit()
    await session.refresh(user)

    return user

# -------------------------------------------------------------------
# DELETE
# -------------------------------------------------------------------

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(user)
    await session.commit()

    return {"message": "User deleted"}
