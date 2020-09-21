from enum import Enum
from typing import List, Optional

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
        None, description="New title of the task.", min_length=3, max_length=120
    )
    description: Optional[str] = Field(
        None, description="New description of the task.", min_length=3, max_length=120
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
