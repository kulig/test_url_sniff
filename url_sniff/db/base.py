from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

from ..settings import app_settings, db_settings


Base = declarative_base()


url = URL.create(**db_settings.dict())
async_engine = create_async_engine(
    url,
    echo=app_settings.debug,
)
async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

engine = create_engine(url)
session = sessionmaker(bind=engine)
