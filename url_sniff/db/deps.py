from typing import Callable, AsyncGenerator, AsyncContextManager
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from .base import async_session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию БД."""

    async with async_session() as session:
        yield session


# Контекстный менеджер для сессии БД.
get_session_acm: Callable[[], AsyncContextManager[AsyncSession]] = asynccontextmanager(get_session)
