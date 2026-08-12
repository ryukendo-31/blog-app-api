from fastapi import FastAPI 
from fastapi import status , Response, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional, List
from random import randrange
import psycopg
from psycopg.rows import dict_row 
import time
from . import models, schemas, utils
from sqlalchemy.orm import Session
from .database import engine, sessionLocal, get_db
from .router import post, users, auth
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
models.Base.metadata.create_all(bind = engine)

app = FastAPI()

while True:
    try:
        conn = psycopg.connect(
            host = 'localhost', 
            dbname = 'fastapi', 
            user = 'postgres',
            password = 'apple',
            row_factory= dict_row
        )
        cursor = conn.cursor()
        print("database connected successfully")
        break
    except Exception as error:
        print("connecting to database failed!")
        print("Error: ", error)
        time.sleep(2)


app.include_router(post.router)
app.include_router(users.router)
app.include_router(auth.router)


