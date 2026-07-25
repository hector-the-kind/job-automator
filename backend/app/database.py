from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# Sanitize DATABASE_URL for asyncpg compatibility (replace sslmode with ssl, remove channel_binding)
db_url = settings.DATABASE_URL
if "postgresql+asyncpg://" in db_url:
    from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
    parsed = urlparse(db_url)
    params = dict(parse_qsl(parsed.query))
    if "sslmode" in params:
        params["ssl"] = params.pop("sslmode")
    params.pop("channel_binding", None)
    new_query = urlencode(params)
    parsed = parsed._replace(query=new_query)
    db_url = urlunparse(parsed)

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
