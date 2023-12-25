from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from .database import get_db
from . import repo

security = HTTPBasic()

class AuthHandler:
    def __init__(self):
        self.db = next(get_db())

    def authenticate_user(self, credentials: HTTPBasicCredentials = Depends(security)):
        user = repo.get_user_by_email(self.db, credentials.username)
        if user and credentials.password + "fakehash" == user.hashed_password:
            return user
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    def check_existing_user(self, db, user_id):
        user = repo.get_user(db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} does not exist")
        return user
