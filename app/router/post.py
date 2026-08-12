from .. import schemas, models
from ..database import get_db ,sessionLocal
from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi import status , Response, HTTPException, Depends
from typing import Optional, List
router = APIRouter(
    prefix= "/posts",
    tags= ['Posts']
)

@router.get("/",response_model= List[schemas.Post])
def get_posts(db : Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts""")
    #posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
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


@router.get("/{id}",response_model= schemas.Post)
def get_post(id: int, response: Response,db : Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""",(id,))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail =f'post with id:{id} was not found')
    return post



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT,)
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



@router.put("/{id}",response_model= schemas.Post)
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