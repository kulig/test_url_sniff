"""Модуль схемы БД."""

from typing import Dict, Optional

from sqlalchemy import Column, Integer, JSON, String

from .base import Base
from ..const import STATUS_NEW


class Tasks(Base):
    __tablename__ = 'tasks'

    id: int = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    url: str = Column(String, nullable=False)
    status: int = Column(Integer, nullable=False, default=STATUS_NEW)
    tags: Optional[Dict[str, int]] = Column(JSON, nullable=True)
    scripts: Optional[Dict[str, str]] = Column(JSON, nullable=True)
    error: Optional[str] = Column(String, nullable=True)

    def __init__(self, url: str):
        self.url = url


# Base.metadata.create_all(engine)
