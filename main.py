import uuid
from enum import Enum
from typing import Dict, Optional, List

import uvicorn
from fastapi import Body, FastAPI, Query, Response, status, Path
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


class UpdateTaskModel(BaseModel):
    title: Optional[str] = Field(
        ..., description="New title of the task.", min_length=3, max_length=120
    )
    description: Optional[str] = Field(
        ..., description="New description of the task.", min_length=3, max_length=120
    )
    status: Optional[TaskStatus] = Field(
        TaskStatus.todo, description="New status of the task.")


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
    description="A simple CRUD constructed as part of BigData project.",
)
db = {}


@app.get(
    "/test",
    summary="Healthcheck",
    description= "Basic request to check if network is running"
)
def healthcheck():
    return {"message": "all good"}


@app.get(
    "/tasks",
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
    "/tasks/{task_id}",
    summary="Retrieve specific tasks",
    description="Used to retrieve information of an specific task present on database.",
    response_description="Task Object",
    response_model=Optional[DatabaseTaskModel]
)
def get_specific_task(
    response: Response,
    task_id: UUID1 = Path(
        ...,
        description="Unique ID of the task you're retrieving",
        example=""
    )
):
    global db

    if task_id in db:
        return db[task_id]
    
    response.status_code = 204
    return
    

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
    status_code=204
)
async def delete_task(
    task_id: UUID1 = Path(
        ...,
        description="Unique ID of the task you're patching",
        example=""
    )
):
    global db

    if UUID1(task_id) in db:
        del db[UUID1(task_id)]


@app.patch(
    "/task/{task_id}", 
    summary="Updates task",
    description="Updates task with given Unique Id and new fields (available fields to be updated can be found on model bellow).",
    response_description="Either task with updated values or message showing that no task with given Unique Id was found.",
    response_model=UpdateTaskOut, 
    response_model_exclude_unset=True
)
async def patch_task(
    response: Response,
    task_id: UUID1 = Path(
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
        task.update(**patch.dict(exclude_unset=True))
        dbTask = DatabaseTaskModel(**task)
        db.update({UUID1(task_id): dbTask})
        return dbTask

    response.status_code = status.HTTP_304_NOT_MODIFIED
    return {"message": f"no task with id {task_id}"}
