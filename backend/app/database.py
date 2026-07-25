from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# Sanitize DATABASE_URL for asyncpg which doesn't support the 'sslmode' query param (expects 'ssl')
db_url = settings.DATABASE_URL
if "postgresql+asyncpg://" in db_url and "sslmode=" in db_url:
    db_url = db_url.replace("sslmode=", "ssl=")

engine = create_async_engine(db_url, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
