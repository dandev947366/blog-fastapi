from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Blogs
from database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
        
db_dependency = Annotated[Session, Depends(get_db)]

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
async def read_all(db: db_dependency):
    return db.query(Blogs).all()
    
@router.get("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
async def read_blog(db: Session = Depends(get_db), blog_id: int = Path(..., gt=0)):
    blog_model = db.query(Blogs).filter(Blogs.id == blog_id).first()
    if blog_model:
        return blog_model
    raise HTTPException(status_code=404, detail="Blog not found")

@router.post("/blog", status_code=status.HTTP_201_CREATED)
async def create_blog(db:db_dependency, blog_request: BlogRequest):
    blog_model = Blogs(**blog_request.dict())
    db.add(blog_model)
    db.commit()
    
@router.put("/blog/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_blog(blog_id: int, blog_request: BlogRequest, db: Session = Depends(get_db)):
    blog_model = db.query(Blogs).filter(Blogs.id == blog_id).first()
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
async def delete_blog(db:db_dependency, blog_id: int = Path(gt=0)):
    blog_model = db.query(Blogs).filter(Blogs.id == blog_id).first()
    if blog_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    db.query(Blogs).filter(Blogs.id == blog_id).delete()
    db.commit()