from .. import schemas, models, oauth2
from ..database import get_db ,sessionLocal
from sqlalchemy.orm import Session
from fastapi import APIRouter
from sqlalchemy import func
from fastapi import status , Response, HTTPException, Depends
from typing import Optional, List

router = APIRouter(
    prefix= "/posts",
    tags= ['Posts']
)

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):

    results = (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("votes")
        )
        .join(
            models.Vote,
            models.Vote.post_id == models.Post.id,
            isouter=True
        )
        .filter(
            models.Post.title.contains(search)
        )
        .group_by(models.Post.id)
        .limit(limit)
        .offset(skip)
        .all()
    )

    return [
        {
            "post": post,
            "votes": votes
        }
        for post, votes in results
    ]


@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post: schemas.PostCreate,db : Session = Depends(get_db), current_user : int =Depends(oauth2.get_current_user) ):
    
    new_post = models.Post(owner_id = current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    result = (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("votes")
        )
        .join(
            models.Vote,
            models.Vote.post_id == models.Post.id,
            isouter=True
        )
        .filter(models.Post.id == id)
        .group_by(models.Post.id)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id:{id} was not found"
        )

    post, votes = result

    return {
        "post": post,
        "votes": votes
    }



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT,)
def delete_post(id: int, db: Session = Depends(get_db), current_user : int =Depends(oauth2.get_current_user)):

    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Not authorised to perform this action ")
    post_query.delete(synchronize_session = False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.put("/{id}",response_model= schemas.Post)
def update_post(id: int, post : schemas.PostCreate, db: Session = Depends(get_db), current_user : int =Depends(oauth2.get_current_user)):
    
    updated_posts = db.query(models.Post).filter(models.Post.id == id)
    db_post = updated_posts.first()
    if db_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )
    if db_post.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Not authorised to perform this action ")
    updated_posts.update(post.model_dump(),synchronize_session = False)
    db.commit()
    return updated_posts.first()