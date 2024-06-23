from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Blogs, Users
from database import SessionLocal
from .auth import get_current_user

router = APIRouter()
router = APIRouter(
    prefix="/user",
    tags=["user"]
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
    
@router.get("/blogs/{user_id}", status_code=status.HTTP_200_OK)
async def read_user_info(user: user_dependency, db: db_dependency, user_id: int = Path(..., gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    user_model = db.query(Blogs).filter(Users.id == user_id).filter(Users.id==user.get('id')).first()
    if user_model:
        return user_model
    raise HTTPException(status_code=404, detail="User not found")