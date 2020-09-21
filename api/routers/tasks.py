from typing import Optional, List

from fastapi import APIRouter, Body, Depends, Path, Query, Response, status
from pydantic import UUID1

from ..database import DBSession, get_db
from ..models import (DatabaseTaskModel, InputTaskModel, UpdateTaskModel,
                    UpdateTaskOut, TaskStatus, Message)

router = APIRouter()


@router.get(
    "/test",
    summary="Healthcheck",
    description="Basic request to check if network is running"
)
def healthcheck():
    return {"message": "all good"}


@router.get(
    "",
    summary="Retrieve tasks",
    description="Used to retrieve information of tasks present on database. You can filter the request based on the status wanted",
    response_description="List which contains all tasks based on the status wanted (all tasks created if no status sent)",
    response_model=List[DatabaseTaskModel]
)
def get_task(
    status: Optional[TaskStatus] = Query(
        None, description="Filter tasks by status."),
    db: DBSession = Depends(get_db)
):

    return db.read_task(status=status)


@router.get(
    "/{task_id}",
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
    ),
    db: DBSession = Depends(get_db)
):

    return db.read_task(uuid=task_id)


@router.post(
    "",
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
    ),
    db: DBSession = Depends(get_db)
):

    return db.create_task(task)


@router.delete(
    "/{task_id}",
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
        description="Unique ID of the task you're deleting",
        example="e4782a82-f38e-11ea-85fc-acde48001122"
    ),
    db: DBSession = Depends(get_db)
):

    return db.delete_task(task_id)


@router.patch(
    "/{task_id}",
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
    ),
    db: DBSession = Depends(get_db)
):

    return db.update_task(modified_task=patch, uuid=task_id)
