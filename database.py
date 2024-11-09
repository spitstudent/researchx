from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from config import settings

SQLALCHEMY_DATABASE_URL = 'postgresql://postgre:stQ7DDrgF7LKwdFaH3y9ng2H626zIwuq@dpg-csnn3b9u0jms738tbmig-a.oregon-postgres.render.com/researchx'


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
