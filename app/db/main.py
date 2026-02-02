from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, Field
from app.config import config
import app.db.models

url = config.DATABASE_URL
engine =  create_async_engine(url, echo = True)

async_session = sessionmaker( 
    bind=engine,
    class_= AsyncSession,
    expire_on_commit= False
)

# async def init_db():
#     async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.create_all) # do we need this anymore? when using alembic? A:no
        #so this can be used to create initial tables before alembic takes over
        #we will comment it out after first run
        #we don't need this code to create tables if we are using alembic for migrations


#i have to understand how this is working
async def get_session():
    async with async_session() as session:
        yield session
