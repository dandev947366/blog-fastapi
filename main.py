from fastapi import FastAPI, Depends, HTTPException, Path, status
from typing import Annotated
from sqlalchemy.orm import Session
import models
from models import Blogs
from database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
        
db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Blogs).all()
    
@app.get("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
async def read_blog(db: Session = Depends(get_db), blog_id: int = Path(..., gt=0)):
    blog_model = db.query(Blogs).filter(Blogs.id == blog_id).first()
    if blog_model:
        return blog_model
    raise HTTPException(status_code=404, detail="Blog not found")
