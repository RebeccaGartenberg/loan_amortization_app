from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import repo, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = repo.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return repo.create_user(db=db, user=user)

@app.post("/users/{user_id}/loans", response_model=schemas.Loan)
def create_loan(loan: schemas.LoanCreate, user_id: int, db: Session = Depends(get_db)):
    db_user = repo.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail=f"User with id {user_id} does not exist")
    return repo.create_user_loan(db=db, loan=loan, user_id=user_id)
