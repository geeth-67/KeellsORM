from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


DATABASE_URL = "postgresql+asyncpg://cclarke:admin@localhost:5432/keells"


engine = create_async_engine(
    DATABASE_URL,
    echo=False,         #set to true if you want to see sql statements produced by orm
    pool_pre_ping=True,     #verify the connections in pool before using then
    future=True,
)

