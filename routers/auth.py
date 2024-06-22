from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from models import Users
from passlib.context import CryptContext

router = APIRouter()
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    role: str
    
@router.post("/auth/")
async def create_user(create_user_request: CreateUserRequest):
    password = bcrypt_context.hash(create_user_request.password)

    new_user = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=password,
        role=create_user_request.role,
        is_active=True
    )

    return new_user 
