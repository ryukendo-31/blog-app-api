from fastapi import FastAPI 
from fastapi import status , Response, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg
from psycopg.rows import dict_row 
import time
from . import models, schemas
from sqlalchemy.orm import Session
from .database import engine, sessionLocal, get_db
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

@app.get("/")
async def root():
    return {"message": "welcome"}


@app.get("/posts",response_model= List[schemas.Post])
def get_posts(db : Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts""")
    #posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post: schemas.PostCreate,db : Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title , content, published) VALUES (%s,%s,%s) RETURNING *"""
    #                ,(post.title, post.content, post.published))
    
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{id}",response_model= schemas.Post)
def get_post(id: int, response: Response,db : Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""",(id,))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail =f'post with id:{id} was not found')
    return post



@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT,)
def delete_post(id: int, db: Session = Depends(get_db)):

    # cursor.execute("""DELETE FROM posts WHERE  id = %s returning * """,(id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)


    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )
    post.delete(synchronize_session = False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.put("/posts/{id}",response_model= schemas.Post)
def update_post(id: int, post : schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute(""" UPDATE posts  SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, id,) )
    # updated_posts = cursor.fetchone()
    # conn.commit()
    updated_posts = db.query(models.Post).filter(models.Post.id == id)
    db_post = updated_posts.first()
    if db_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )
    updated_posts.update(post.model_dump(),synchronize_session = False)
    db.commit()
    return updated_posts.first()
