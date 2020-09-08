from fastapi import FastAPI, Query, Body
from pydantic import BaseModel, Field, ValidationError, validator, UUID1
from typing import Optional, Dict
from enum import Enum
import uvicorn
import uuid


class TaskStatus(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class InputTaskModel(BaseModel):
    title: str = Field(
        ..., description="Title of the task.", min_length=3, max_length=120
    )
    description: str = Field(
        ..., description="Description of the task.", min_length=3, max_length=120
    )


class DatabaseTaskModel(BaseModel):
    uuid: UUID1 = Field(..., description="UUID of the newly created task.")
    title: str = Field(
        ..., description="Title of the task.", min_length=3, max_length=120
    )
    description: str = Field(
        ..., description="Description of the task.", min_length=3, max_length=120
    )
    status: TaskStatus = Field(TaskStatus.todo, description="Status of the task.")

class UpdateTaskModel(BaseModel):
    title: Optional[str] = Field(
        ..., description="New title of the task.", min_length=3, max_length=120
    )
    description: Optional[str] = Field(
        ..., description="New description of the task.", min_length=3, max_length=120
    )
    status: Optional[TaskStatus] = Field(TaskStatus.todo, description="New status of the task.")

class UpdateTaskOut(BaseModel):
    title: Optional[str] = Field(
        None, description="New title of the task."
    )
    description: Optional[str] = Field(
        None, description="New description of the task."
    )
    status: Optional[TaskStatus] = Field(
        None, description="New status of the task."
    )
    message: Optional[str] = Field(
        None, description="This item appears in the situation of nonexistent task with the given UUID."
    )

app = FastAPI(
    title="Nollo CRUD",
    description="CRUD Simples para a APS1 da disciplina de Megadados.",
)
db = {}


@app.get("/test")
def healthcheck():
    return {"message": "all good"}


@app.get("/tasks")
def get_task(
    status: Optional[TaskStatus] = Query(None, description="Filter tasks by status.")
):
    global db

    if status != None:
        return [
            task for task in db.values() if task.status == status
        ]

    return [task for task in db.values()]


@app.post("/task", response_model=DatabaseTaskModel)
async def create_task(
    task: InputTaskModel = Body(
        ...,
        description="Task to be added.",
        example={
            "title": "Random task title",
            "description": "Random task description",
        },
    )
):
    global db

    dbTask = DatabaseTaskModel(**task.dict(), uuid=uuid.uuid1())
    if dbTask.uuid not in db:
        db.update({dbTask.uuid: dbTask})
        return dbTask

@app.delete("/task/{task_id}")
async def delete_task(
    task_id: str = Query(
        ...,
        description="Unique ID of the task you're patching",
        example=""
    )
):
    global db

    if UUID1(task_id) in db:
        del db[UUID1(task_id)]

@app.patch("/task/{task_id}", response_model=UpdateTaskOut)
async def patch_task(
    task_id: str = Query(
        ...,
        description="Unique ID of the task you're patching",
        example=""
    ),
    patch: UpdateTaskModel = Body(
        ...,
        description="Fields to be updated.",
        example={
            "title": "New Title",
            "description": "New Description",
            "status": "doing"
        }
    )
):
    global db

    task = db.get(UUID1(task_id))
    if task is not None:
        task = task.dict()
        task.update(**patch.dict())
        dbTask = DatabaseTaskModel(**task)
        db.update({UUID1(task_id): dbTask})
        return dbTask
        
    return {"message": f"no task with id {task_id}"}
