import os
from passlib.context import CryptContext
import jwt
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd.verify(plain, hashed)

def create_token(user_id: int) -> str:
    payload = {"sub": user_id}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
