import asyncio
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


# Async database URL
postgres_url = "postgresql+asyncpg://postgres:1729@localhost:5432/newdb"

# Create async engine
async_engine = create_async_engine(postgres_url, echo=True)

# Async session factory (IMPORTANT FIX)
async_session = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_and_read_heroes():
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Insert and read data
    async with async_session() as session:
        # Insert
        hero = Hero(name="keerthi", secret_name="suresh", age=21)
        session.add(hero)
        await session.commit()

        # Read
        statement = select(Hero).order_by(Hero.name).limit(2)
        result = await session.exec(statement)
        heroes = result.all()

        print("\nHeroes from Async Postgres:")
        for hero in heroes:
            print(hero)


# Run the async function
if __name__ == "__main__":
    asyncio.run(create_and_read_heroes())
