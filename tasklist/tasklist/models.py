# pylint: disable=missing-module-docstring,missing-class-docstring
from typing import Optional

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


# pylint: disable=too-few-public-methods
class Task(BaseModel):
    description: Optional[str] = Field(
        'no description',
        title='Task description',
        max_length=1024,
    )
    completed: Optional[bool] = Field(
        False,
        title='Shows whether the task was completed',
    )
    user: Optional[str] = Field(
        None,
        title='User`s username',
        max_length=40,
    )

    class Config:
        schema_extra = {
            'example': {
                'description': 'Buy baby diapers',
                'completed': False,
            }
        }

# pylint: disable=too-few-public-methods
class User(BaseModel):
    username: Optional[str] = Field(
        None,
        title='User`s username',
        max_length=40,
    )
    first_name: Optional[str] = Field(
        'User`s firstname',
        title='User`s firstname',
        max_length=20,
    )
    last_name: Optional[str] = Field(
        'User`s lastname',
        title='User`s lastname',
        max_length=20,
    )

    class Config:
        schema_extra = {
            'example': {
                'username': 'john_doe',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        }

