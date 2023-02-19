from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .base import async_session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию БД."""

    async with async_session() as session:
        yield session
