import uuid
from enum import Enum
from typing import Dict, List, Optional

import uvicorn
from fastapi import Body, FastAPI, HTTPException, Path, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import UUID1, BaseModel, Field, ValidationError, validator


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

    class Config:
        schema_extra = {
            "example": {
                "title": "Random task title",
                "description": "Random task description"
            }
        }


class DatabaseTaskModel(BaseModel):
    uuid: UUID1 = Field(..., description="UUID of the newly created task.")
    title: str = Field(
        ..., description="Title of the task.", min_length=3, max_length=120
    )
    description: str = Field(
        ..., description="Description of the task.", min_length=3, max_length=120
    )
    status: TaskStatus = Field(
        TaskStatus.todo, description="Status of the task.")

    class Config:
        schema_extra = {
            "example": {
                "uuid": "e4782a82-f38e-11ea-85fc-acde48001122",
                "title": "Random task title",
                "description": "Random task description",
                "status": "todo"
            }
        }


class UpdateTaskModel(BaseModel):
    title: Optional[str] = Field(
        ..., description="New title of the task.", min_length=3, max_length=120
    )
    description: Optional[str] = Field(
        ..., description="New description of the task.", min_length=3, max_length=120
    )
    status: Optional[TaskStatus] = Field(
        TaskStatus.todo, description="New status of the task.")

    class Config:
        schema_extra = {
            "example": {
                "title": "Random task title",
                "description": "Random task description",
                "status": "todo"
            }
        }


class Message(BaseModel):
    message: str

    class Config:
        schema_extra = {
            "example": {
                "message": "Task not found."
            }
        }


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


app = FastAPI(
    title="Nollo CRUD",
    description="A simple CRUD constructed as part of BigData project.",
)
db = {}


@app.get(
    "/test",
    summary="Healthcheck",
    description="Basic request to check if network is running"
)
def healthcheck():
    return {"message": "all good"}


@app.get(
    "/task",
    summary="Retrieve tasks",
    description="Used to retrieve information of tasks present on database. You can filter the request based on the status wanted",
    response_description="List which contains all tasks based on the status wanted (all tasks created if no status sent)",
    response_model=List[DatabaseTaskModel]
)
def get_task(
    status: Optional[TaskStatus] = Query(
        None, description="Filter tasks by status.")
):
    global db

    if status != None:
        return [
            task for task in db.values() if task.status == status
        ]

    return [task for task in db.values()]


@app.get(
    "/task/{task_id}",
    summary="Retrieve specific tasks",
    description="Used to retrieve information of an specific task present on database.",
    response_description="Task Object",
    response_model=Optional[DatabaseTaskModel],
    responses={
        404: {
            "description": "Task not found",
            "model": Message
        }
    }
)
def get_specific_task(
    response: Response,
    task_id: UUID1 = Path(
        ...,
        description="Unique ID of the task you're retrieving",
        example="e4782a82-f38e-11ea-85fc-acde48001122"
    )
):
    global db

    if task_id in db:
        return db[task_id]

    return JSONResponse(status_code=404, content={"message": "Task not found"})


@app.post(
    "/task",
    summary="Create task",
    description="Creates a task with specific title and description. All tasks are created with a default status, set to 'todo'",
    response_description="Task inserted into database, which contains its Unique Id, used to perform Patch and Delete requests.",
    response_model=DatabaseTaskModel,
    status_code=201
)
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


@app.delete(
    "/task/{task_id}",
    summary="Removes task",
    description="Removes task from database, based on given Unique Id. If that Unique Id does not exist on DB, nothing is done",
    status_code=204,
    responses={
        404: {
            "description": "Task not found",
            "model": Message
        }
    }
)
async def delete_task(
    task_id: UUID1 = Path(
        ...,
        description="Unique ID of the task you're patching",
        example="e4782a82-f38e-11ea-85fc-acde48001122"
    )
):
    global db

    if task_id in db:
        del db[task_id]
        return

    return JSONResponse(status_code=404, content={"message": "Task not found"})


@app.patch(
    "/task/{task_id}",
    summary="Updates task",
    description="Updates task with given Unique Id and new fields (available fields to be updated can be found on model bellow).",
    response_description="Task with updated values.",
    response_model=UpdateTaskOut,
    responses={
        404: {
            "description": "Task not found",
            "model": Message
        }
    }
)
async def patch_task(
    response: Response,
    task_id: UUID1 = Path(
        ...,
        description="Unique ID of the task you're patching",
        example="e4782a82-f38e-11ea-85fc-acde48001122"
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

    task = db.get(task_id)
    if task is not None:
        task = task.dict()
        task.update(**patch.dict(exclude_unset=True))
        dbTask = DatabaseTaskModel(**task)
        db.update({task_id: dbTask})
        return dbTask

    return JSONResponse(status_code=404, content={"message": "Task not found"})
