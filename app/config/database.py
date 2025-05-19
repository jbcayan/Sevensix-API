from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

if settings.DATABASE_TYPE.lower() == "sqlite3":
    async_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "sqlite+aiosqlite:///")
elif settings.DATABASE_TYPE.lower() == "postgres":
    async_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://")
else:
    async_db_url = settings.SQLALCHEMY_DATABASE_URI

engine = create_async_engine(
    async_db_url,
    future=True,
    echo=False,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
