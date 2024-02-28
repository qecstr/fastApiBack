import sqlalchemy as sql
from fastapi import FastAPI, Depends
from fastapi.openapi.models import Response

from pydantic import BaseModel
import app.Models as Models
from typing import Annotated
from app.database import engine, SessionLocal
from sqlalchemy.orm import Session
import datetime

from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
Models.Base.metadata.create_all(bind=engine)
finances = sql.Table('Finances', sql.MetaData(), autoload_with=engine)
origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Finances(BaseModel):
    date: datetime.date
    operation_type: str
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
    db_Finances = Models.Finances(date=Finances.date, operation_type=Finances.operation_type, sum=Finances.sum,
                                  sender=Finances.sender,
                                  comment=Finances.comment)
    db.add(db_Finances)
    db.commit()
    db.refresh(db_Finances)


@app.get("/finances/{id}")
async def get(id: int, db: db_dependency):
   
    query = db.query(Models.Finances).filter(Models.Finances.id == id).first()
    return query


@app.get("/financesAll")
async def getAll(db: db_dependency):
    query = db.query(Models.Finances).all()
    return query
@app.post("/financeUpdate/{id}")
async def update(Finances: Finances ,db :db_dependency,id:int ):

    query = db.query(Models.Finances).filter(Models.Finances.id == id).first()
    query.date=Finances.date
    query.operation_type = Finances.operation_type
    query.sum = Finances.sum
    query.sender = Finances.sender
    query.comment = Finances.comment
    db.commit()
    db.refresh(query)

@app.delete("/financesDelete/{id}")
async def delete(db: db_dependency,id:int ):
    query = db.query(Models.Finances).filter(Models.Finances.id == id).first()
    db.delete(query)
    db.commit()
