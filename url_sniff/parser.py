from typing import Optional
from collections import Counter

import requests
from bs4 import BeautifulSoup

from .db.models import Tasks
from .db import session


def parser(task_id: int) -> None:
    sess = session()
    task: Optional[Tasks] = sess.query(Tasks).get(task_id)
    if task is None:
        return

    resp = requests.get(task.url, allow_redirects=True, timeout=5)
    bs = BeautifulSoup(resp.text, "html.parser")
    task.tags = dict(Counter([i.name for i in bs.find_all()]).items())
    task.status = 1
    sess.add(task)
    sess.commit()
