from pydantic import BaseModel, HttpUrl


class TaskIn(BaseModel):
    url: HttpUrl


class TaskOut(BaseModel):
    task_id: int
