from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Blogs
from database import SessionLocal
from .auth import get_current_user

router = APIRouter()
router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/blog", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db:db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Blogs).all()
        
        