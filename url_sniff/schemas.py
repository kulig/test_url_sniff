"""Схемы Pydantic"""

from fastapi import Path
from typing import Dict, Optional

from pydantic import BaseModel, HttpUrl


class TaskIn(BaseModel):
    url: HttpUrl = Path(title="URL для парсинга")


class TaskOut(BaseModel):
    task_id: int = Path(title="ID задачи")


class TaskInfoOut(BaseModel):
    id: Optional[int] = Path(title="ID задачи")
    url: Optional[HttpUrl] = Path(title="URL задачи")
    status: Optional[int] = Path(title="Статус задачи")
    tags: Optional[Dict[str, int]] = Path(title="Тэги")
    scripts: Optional[Dict[str, str]] = Path(title="Скрипты")
    error: Optional[str] = Path(title="Текст ошибки")
