import uuid

from typing import Dict

from fastapi import APIRouter, HTTPException, Depends

from ..database import DBSession, get_db
from ..models import User

router = APIRouter()

@router.get(
    '/{username}',
    summary='Reads user',
    description='Reads User from username.',
    response_model=User,
)
async def read_user(username: str, db: DBSession = Depends(get_db)):
    try:
        return db.read_user(username)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='User not found',
        ) from exception

@router.post(
    '',
    summary='Creates a new user',
    description='Creates a new user and returns its username.',
    response_model=str,
)
async def create_user(user: User, db: DBSession = Depends(get_db)):
    return db.create_user(user)

@router.put(
    '/{username}',
    summary='Replaces a user',
    description='Replaces a user identified by its username.',
)
async def replace_user(
        username: str,
        user: User,
        db: DBSession = Depends(get_db),
):
    try:
        db.replace_user(username, user)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='User not found',
        ) from exception

@router.patch(
    '/{username}',
    summary='Alters user',
    description='Alters a user identified by its username',
)
async def alter_user(
        username: str,
        item: User,
        db: DBSession = Depends(get_db),
):
    try:
        old_item = db.read_user(username)
        update_data = item.dict(exclude_unset=True)
        new_item = old_item.copy(update=update_data)
        db.replace_user(username, new_item)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='User not found',
        ) from exception

@router.delete(
    '/{username}',
    summary='Deletes user',
    description='Deletes a user identified by its username',
)
async def remove_user(username: str, db: DBSession = Depends(get_db)):
    try:
        db.remove_user(username)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='User not found',
        ) from exception


@router.delete(
    '',
    summary='Deletes all users, use with caution',
    description='Deletes all users, use with caution',
)
async def remove_all_users(db: DBSession = Depends(get_db)):
    db.remove_all_users()