"""Пул обработки задач."""

from asyncio import Task, sleep, create_task
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import select, func, update

from .db import get_session_acm
from .db.models import Tasks
from .const import STATUS_PROCESS, STATUS_NEW
from .parser import parser


class WorkerPool:
    """Класс реализации асинхронной обработки задач."""

    def __init__(self, max_workers: int):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._task: Optional[Task[None]] = None

    def start(self) -> None:
        """Создает главную задачу."""

        self._task = create_task(self._run())

    def shutdown(self) -> None:
        """Остановливает обработку пула задач."""

        if self._task is not None:
            self._task.cancel()
        self.executor.shutdown()

    async def _run(self) -> None:
        """Цикл обработки пула задач."""
        await self._reset()

        while True:
            async with get_session_acm() as db_session:
                # Подсчитываем сколько задач в обработке во избежание создания потенциально большого кол-ва задач.
                in_work: int = await db_session.scalar(
                    select(func.count(Tasks.id)).where(Tasks.status == STATUS_PROCESS),
                ) or 0
                for t in await db_session.scalars(
                    select(Tasks).where(Tasks.status == STATUS_NEW).limit(self.max_workers - in_work),
                ):
                    t.status = STATUS_PROCESS
                    db_session.add(t)
                    await db_session.commit()
                    self.executor.submit(parser, t.id)

            # Немного спим)
            await sleep(1)

    @staticmethod
    async def _reset() -> None:
        """Сброс всех незавершенных задач."""

        async with get_session_acm() as db_session:
            await db_session.execute(
                update(Tasks).where(Tasks.status == STATUS_PROCESS).values({Tasks.status: STATUS_NEW}),
            )
            await db_session.commit()
