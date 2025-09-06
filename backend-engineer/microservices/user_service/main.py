from fastapi import FastAPI, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User
from schemas import UserCreate, UserOut, LoginRequest, TokenResponse
from auth import hash_password, verify_password, create_token
import os
import redis
import json
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

app = FastAPI(title="User Service")
Base.metadata.create_all(bind=engine)

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=payload.email).first():
        raise HTTPException(400, "Email already registered")
    u = User(email=payload.email, password_hash=hash_password(payload.password), full_name=payload.full_name)
    db.add(u)
    db.commit()
    db.refresh(u)
    # publish event
    event = {"type": "user_created", "user_id": u.id, "email": u.email}
    r.publish("user_events", json.dumps(event))
    return u

@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    u = db.query(User).filter_by(email=payload.email).first()
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return TokenResponse(access_token=create_token(u.id))

@app.get("/users/me", response_model=UserOut)
def me(x_user_id: str = Header(None), db: Session = Depends(get_db)):

    if not x_user_id:
        raise HTTPException(401, "Not authenticated")
    u = db.get(User, int(x_user_id))
    if not u:
        raise HTTPException(404, "User not found")
    return u
