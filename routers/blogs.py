from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Blogs
from database import SessionLocal
from .auth import get_current_user

router = APIRouter()
router = APIRouter(
    prefix="/blogs",
    tags=["blogs"]
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class BlogRequest(BaseModel):
    title: str
    description: str
    priority: int
    complete: bool

class BlogRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
    
    
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Blogs).filter(Blogs.owner_id==user.get('id')).all()
    
@router.get("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
async def read_blog(user: user_dependency, db: Session = Depends(get_db), blog_id: int = Path(..., gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    blog_model = db.query(Blogs).filter(Blogs.id == blog_id).filter(Blogs.id==user.get('id')).first()
    if blog_model:
        return blog_model
    raise HTTPException(status_code=404, detail="Blog not found")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_blog(user: user_dependency, db: db_dependency, blog_request: BlogRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    blog_model = Blogs(**blog_request.dict(), owner_id=user.get('id'))
    db.add(blog_model)
    db.commit()
    db.refresh(blog_model)
    return blog_model
    
@router.put("/blog/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_blog(user: user_dependency, db: db_dependency, blog_request: BlogRequest, blog_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    blog_model = db.query(Blogs).filter(Blogs.id == blog_id).filter(Blogs.owner_id==user.get('id')).filter(Blogs.owner_id).first()
    if blog_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    blog_model.title = blog_request.title
    blog_model.description = blog_request.description
    blog_model.priority = blog_request.priority
    blog_model.complete = blog_request.complete

    db.add(blog_model)
    db.commit()

    return {"message": "Blog updated successfully"}
    
@router.delete("/blog/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(user: user_dependency, db:db_dependency, blog_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    blog_model = db.query(Blogs).filter(Blogs.owner_id==user.get('id')).filter(Blogs.id == blog_id).first()
    if blog_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    db.query(Blogs).filter(Blogs.id == blog_id).delete()
    db.commit()