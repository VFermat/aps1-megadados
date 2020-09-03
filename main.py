from typing import Optional

from fastapi import Body, FastAPI, Path, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Nollo CRUD",
    description="CRUD Simples para a APS1 da disciplina de Megadados."
)

@app.get("/test")
def route():
    return {"message": "all good"}
