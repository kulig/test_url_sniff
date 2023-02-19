"""Модуль базового подключения к БД."""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

from ..settings import app_settings, db_settings


Base = declarative_base()


# Для синхронного использования
url_sync = URL.create(
    drivername='postgresql+psycopg2',
    **db_settings.dict(),
)
engine = create_engine(url_sync)
session = sessionmaker(bind=engine)


# Для асинхронного использования
url_async = URL.create(
    drivername='postgresql+asyncpg',
    **db_settings.dict(),
)
async_engine = create_async_engine(
    url_async,
    echo=app_settings.debug,
)
async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
