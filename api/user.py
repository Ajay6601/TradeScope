from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from db.models import User
from db.db_connection import get_db
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from datetime import timedelta
from api.auth import verify_password, create_access_token

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Set token expiry

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utility function to hash passwords
def get_password_hash(password):
    return pwd_context.hash(password)


# Login an existing user
@router.post("/login")
async def login_user(username: str, password: str, db: AsyncSession = Depends(get_db)):
    # Check if the user exists
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

# Register a new user
@router.post("/register")
async def register_user(username: str, password: str, email: str, db: AsyncSession = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, password=hashed_password, email=email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User registered successfully!"}



