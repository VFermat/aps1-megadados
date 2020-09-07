from fastapi import FastAPI, Query, Body
from pydantic import BaseModel, Field, ValidationError, validator
from typing import Optional
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
    title: str = Field(
        ..., description="Title of the task.", min_length=3, max_length=120
    )
    description: str = Field(
        ..., description="Description of the task.", min_length=3, max_length=120
    )
    status: TaskStatus = Field(TaskStatus.todo, description="Status of the task.")


app = FastAPI(
    title="Nollo CRUD",
    description="CRUD Simples para a APS1 da disciplina de Megadados.",
)
db = {}


@app.get("/test")
def route():
    return {"message": "all good"}


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

    task_uuid = uuid.uuid1()
    dbTask = DatabaseTaskModel(**task.dict())
    if task_uuid not in db:
        db.update({task_uuid: dbTask})

    return db