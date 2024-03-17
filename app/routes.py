from fastapi import FastAPI, Depends
from fastapi import APIRouter
from typing import Annotated

from pydantic import BaseModel
from sqlalchemy.orm import Session
import app.crud as crud
from app.database import SessionLocal
from app.schemas import EmployeesJson




router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/employee/get/{id}")
async def getByID(id:int,db:db_dependency):
    return crud.getByid(id,db)

@router.post("/employee/create")
async def create(emp:EmployeesJson,db:db_dependency):
    return crud.create(emp,db)
@router.get("/employee/getAll")
async def getAll(db:db_dependency):
    return crud.getAll(db)
@router.post("/employee/update/{id}")
async def update(emp:EmployeesJson,db:db_dependency,id:int):
    return crud.update(emp,db,id)
@router.delete("/employee/delete/{id}")
async def delete(id:int,db:db_dependency):
    return crud.delete(db,id)