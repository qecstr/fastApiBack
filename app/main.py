import sqlalchemy as sql
from fastapi import FastAPI, Depends
from fastapi.openapi.models import Response

from pydantic import BaseModel
import app.Models as Models
from typing import Annotated
from app.database import engine, SessionLocal
from sqlalchemy.orm import Session

import datetime

app = FastAPI()
Models.Base.metadata.create_all(bind=engine)
finances = sql.Table('Finances', sql.MetaData(), autoload_with=engine)


class Finances(BaseModel):
    date: datetime.date
    operatrion_type: str
    sum: float
    sender: str
    comment: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/finances")
async def create_finances(Finances: Finances, db: db_dependency):
    db_Finances = Models.Finances(date=Finances.date, operation_type=Finances.operatrion_type, sum=Finances.sum,
                                  sender=Finances.sender,
                                  comment=Finances.comment)
    db.add(db_Finances)
    db.commit()
    db.refresh(db_Finances)


@app.get("/finances/{id}")
async def get(id: int, db: db_dependency):
   
    query = db.query(Models.Finances).filter(Models.Finances.id == id).first()
    return query


@app.get("/finances/getALL")
async def getAll(db: db_dependency):
    query = db.query(Models.Finances).all()
    return query
