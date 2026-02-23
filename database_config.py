from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


DATABASE_URL = "postgresql+asyncpg://cclarke:admin@localhost:5432/keells"


engine = create_async_engine(
    DATABASE_URL,
    echo=False,         #set to true if you want to see sql statements produced by orm
    pool_pre_ping=True,     #verify the connections in pool before using then
    future=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:       #when i use async the function convert to coroutine function
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()