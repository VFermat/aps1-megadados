import uvicorn
from fastapi import Depends, FastAPI

from .routers import tasks

app = FastAPI(
    title="Nollo CRUD",
    description="A simple CRUD constructed as part of BigData project.",
)
app.include_router(
    tasks.router,
    prefix='/task',
    tags=['task']
)
