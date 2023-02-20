"""Модуль АПИ"""

import logging
from typing import Optional, Dict

from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import _TemplateResponse

from .db import get_session
from .db.models import Tasks
from .settings import app_settings
from .schemas import TaskIn, TaskOut, TaskInfoOut
from .worker_pool import WorkerPool
from .const import STATUS_NEW


app = FastAPI(
    debug=app_settings.debug,
)


logging.basicConfig(level=logging.DEBUG)


templates = Jinja2Templates(directory="url_sniff/templates")


@app.get("/")
def root() -> str:
    """
    Просто заглушка для главное страницы.
    """

    return "Парсинг URL-адресов."


@app.post("/tasks/parse_page")
async def parse_page(
        task_url: TaskIn,
        db_session: AsyncSession = Depends(get_session),
) -> TaskOut:
    """
    Создает задачу на парсинг URL. Возвращает ID созданной задачи.

    :param task_url: URL.
    :param db_session: Сессия БД.
    """

    # Проверяем имеется ли уже в очереди на обработку передаваемый адрес.
    # Избегаем "залипания" на передачу одного и того же адреса.

    data: Optional[Tasks] = (
        await db_session.scalars(
            select(Tasks).where(
                and_(
                    (Tasks.url == task_url.url),
                    (Tasks.status == STATUS_NEW),
                ),
            ).limit(1),
        )
    ).first()
    if data is not None:
        return TaskOut(task_id=data.id)

    # Регистрируем задачу.
    task: Tasks = Tasks(task_url.url)
    db_session.add(task)
    await db_session.flush()
    await db_session.commit()

    return TaskOut(task_id=task.id)


@app.get("/tasks/{task_id}", response_class=JSONResponse)
async def get_task(
        task_id: int,
        db_session: AsyncSession = Depends(get_session),
) -> TaskInfoOut:
    """
    Получить результат парсинга адреса.

    :param task_id: ID задачи.
    :param db_session: Сессия БД.
    """

    task: Optional[Tasks] = (
        await db_session.scalars(
            select(Tasks).where(Tasks.id == task_id),
        )
    ).first()
    if task is None:
        return TaskInfoOut()

    return TaskInfoOut(
        id=task.id,
        status=task.status,
        url=task.url,
        tags=task.tags,
        scripts=task.scripts,
        error=task.error,
    )


@app.get("/tasks/{task_id}/html", response_class=HTMLResponse)
async def get_task_html(
        request: Request,
        task_id: int,
        db_session: AsyncSession = Depends(get_session),
) -> _TemplateResponse:
    """
    Формирует результат парсинга в виде HTML страницы.

    :param request: Request.
    :param task_id: ID задачи.
    :param db_session: Сессия БД.
    """

    task: TaskInfoOut = await get_task(task_id, db_session)

    return templates.TemplateResponse(
        "task_info.html",
        {
            "request": request,
            "data": task.dict(),
        },
    )


@app.get("/tasks/{task_id}/scripts/{script_id}", response_class=PlainTextResponse)
async def get_script(
        task_id: int,
        script_id: str,
        db_session: AsyncSession = Depends(get_session),
) -> Optional[str]:
    """
    Получить текст скрипта из задачи по парсингу.

    :param task_id: ID задачи.
    :param script_id: ID скрипта.
    :param db_session: Сессия БД.
    """

    scripts: Dict[str, str] = await db_session.scalar(
        select(Tasks.scripts).where(Tasks.id == task_id),
    )

    return scripts.get(script_id)


@app.on_event("startup")
async def schedule_periodic() -> None:
    """
    Создание пула задач на парсинг адресов.
    """

    app.state.worker = WorkerPool(app_settings.max_workers)
    app.state.worker.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Остановка пула задач.
    """

    app.state.worker.shutdown()
