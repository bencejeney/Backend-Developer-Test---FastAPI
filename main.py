# main.py (Routing Layer)
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Post
from crud import create_user, authenticate_user, create_post, get_posts, delete_post
from security import create_access_token, verify_token
from datetime import timedelta

app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserSignup(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class PostCreate(BaseModel):
    text: str

@app.post("/signup", response_model=str)
async def signup(user: UserSignup, db: Session = Depends(get_db)):
    db_user = create_user(db, user.email, user.password)
    return create_access_token(data={"sub": db_user.id})

@app.post("/login", response_model=str)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return create_access_token(data={"sub": db_user.id})

@app.post("/addpost", response_model=int)
async def add_post(post: PostCreate, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    post_id = create_post(db, post.text, token)
    return post_id

@app.get("/getposts", response_model=List[Post])
async def get_user_posts(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    return get_posts(db, token)

@app.delete("/deletepost/{post_id}", response_model=str)
async def delete_user_post(post_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    delete_post(db, post_id, token)
    return "Post deleted successfully"
