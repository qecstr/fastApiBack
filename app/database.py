from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sql
URL_DATABASE = 'postgresql://postgres:postgres@db/postgres'
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit = False,autoflush=False, bind=engine)
Base = declarative_base()
