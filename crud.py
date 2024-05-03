# crud.py (Business Logic Layer)
from sqlalchemy.orm import Session
from models import User, Post
from datetime import datetime, timedelta
from security import hash_password, verify_password
from pydantic import ValidationError
from cachetools import cached, TTLCache

def create_user(db: Session, email: str, password: str):
    hashed_password = hash_password(password)
    db_user = User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_post(db: Session, text: str, token: str):
    # Validate payload size
    if len(text.encode('utf-8')) > (1024 * 1024):  # 1 MB
        raise ValidationError("Payload size exceeds 1 MB limit")
    
    # Assuming token contains user id
    user_id = int(token)  # You may need to decode your JWT token here
    
    post = Post(text=text, user_id=user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post.id

# Define a cache with a TTL (time to live) of 5 minutes
cache = TTLCache(maxsize=100, ttl=300)

@cached(cache)
def get_posts(db: Session, token: str):
    # Assuming token contains user id
    user_id = int(token)  # You may need to decode your JWT token here

    # Fetch posts from the database
    posts = db.query(Post).filter(Post.user_id == user_id).all()

    return posts

def delete_post(db: Session, post_id: int, token: str):
    # Assuming token contains user id
    user_id = int(token)  # You may need to decode your JWT token here

    # Ensure only the owner can delete the post
    db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).delete()
    db.commit()
