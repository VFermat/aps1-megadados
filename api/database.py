import uuid

from fastapi.responses import JSONResponse
from pydantic import UUID1

from .models import (DatabaseTaskModel, InputTaskModel, TaskStatus,
                     UpdateTaskModel)


class DBSession:
    tasks = {}

    def __init__(self):
        self.tasks = DBSession.tasks

    def read_task(self, status: TaskStatus = None, uuid: UUID1 = None):
        if uuid:
            try:
                return self.tasks.get({'uuid': uuid})
            except:
                return JSONResponse(status_code=404, content={"message": "Task not found"})
        if status:
            return [task for task in self.tasks.values() if task.status == status]
        return [task for task in self.tasks.values()]

    def create_task(self, task: InputTaskModel):
        db_task = DatabaseTaskModel(**task.dict(), uuid=uuid.uuid1())
        if db_task.uuid not in self.tasks:
            self.tasks.update({db_task.uuid: db_task})
            return db_task

    def delete_task(self, uuid: UUID1 = None):
        try:
            del self.tasks[uuid]
            return
        except:
            return JSONResponse(status_code=404, content={"message": "Task not found"})

    def update_task(self, modified_task: UpdateTaskModel, uuid: UUID1 = None):
        if uuid in self.tasks:
            task = self.tasks[uuid]
            task = task.dict()
            task.update(**modified_task.dict(exclude_unset=True))
            db_task = DatabaseTaskModel(**task)
            self.tasks.update({uuid: db_task})
            return db_task

        return JSONResponse(status_code=404, content={"message": "Task not found"})


def get_db():
    return DBSession()
