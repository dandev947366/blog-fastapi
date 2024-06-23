from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, EmailStr
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

TEST_SECRET_KEY = '3ffdbcd6f35b28fa6493a8e18205c1b9e6b2c0b721f0a4d952af391adc41176d'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

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

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
    
def create_access_token(username: str, user_id: int, role:str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, TEST_SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends:(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, TEST_SECRET_KEY, ALGORITHM)
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
        

@router.post("/", status_code=status.HTTP_201_CREATED)
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
    
@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    # return 'Success'   
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return token
    
