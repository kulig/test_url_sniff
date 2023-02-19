"""Схемы Pydantic"""

from typing import Dict, Optional

from pydantic import BaseModel, HttpUrl


class TaskIn(BaseModel):
    url: HttpUrl


class TaskOut(BaseModel):
    task_id: int


class TaskInfoOut(BaseModel):
    id: Optional[int]
    url: Optional[HttpUrl]
    tags: Optional[Dict[str, int]]
    scripts: Optional[Dict[str, str]]
    error: Optional[str]
