from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, EmailStr
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from database import engine, SessionLocal
router = APIRouter()
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    role: str
    
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
        
db_dependency = Annotated[Session, Depends(get_db)]
    
@router.post("/auth/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,create_user_request: CreateUserRequest):
    password = bcrypt_context.hash(create_user_request.password)

    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=password,
        role=create_user_request.role,
        is_active=True
    )
    db.add(create_user_model)
    db.commit()
    
    return create_user_model