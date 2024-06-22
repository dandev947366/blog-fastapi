from fastapi import FastAPI, Depends, HTTPException, Path, status
import models
from models import Blogs
from database import engine, SessionLocal
from routers import auth, blogs

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(blogs.router)
