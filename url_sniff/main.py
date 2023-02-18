from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .db import get_session
from .db.models import Tasks
from .settings import app_settings
from .schemas import TaskIn, TaskOut
from .parser import parser

app = FastAPI(
    debug=app_settings.debug,
)


@app.get("/")
def root() -> str:
    return "hello, world"


@app.post("/tasks/parse_page")
async def parse_page(
        task_in: TaskIn,
        background_tasks: BackgroundTasks,
        db_sesion: AsyncSession = Depends(get_session),
) -> TaskOut:
    task: Tasks = Tasks(task_in.url)
    db_sesion.add(task)
    await db_sesion.flush()
    await db_sesion.commit()

    background_tasks.add_task(parser, task.id)
    return TaskOut(task_id=task.id)


@app.get("/tasks/{task_id}")
async def get_task(
        task_id: int,
        db_sesion: AsyncSession = Depends(get_session),
) -> str:
    task: Tasks = (
        await db_sesion.scalars(
            select(Tasks).where(Tasks.id == task_id),
        )
    ).one()

    return task.url
