"""Модуль парсинга URL."""

from typing import Optional
from collections import Counter

import requests
from bs4 import BeautifulSoup

from .db import session
from .db.models import Tasks
from .const import STATUS_DONE, STATUS_ERROR


def parser(task_id: int) -> None:
    """
    Парсинг URL.

    :param task_id: ID задачи.
    :param url: URL.
    """

    with session() as db_session:
        task: Optional[Tasks] = db_session.get(Tasks, task_id)
        if task is None:
            return

        try:
            resp = requests.get(task.url, allow_redirects=True, timeout=10)
            bs = BeautifulSoup(resp.text, "html.parser")
            task.tags = dict(Counter([i.name for i in bs.find_all()]).items())
            task.scripts = {f"script_{n}": str(i) for n, i in enumerate(bs.find_all("script"), 1)}
            task.status = STATUS_DONE
            task.error = None
        except Exception as err:
            task.status = STATUS_ERROR
            task.error = str(err)
        finally:
            db_session.add(task)
            db_session.commit()
