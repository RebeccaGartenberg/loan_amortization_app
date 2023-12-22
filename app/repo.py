from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "fakehash"
    db_user = models.User(email=user.email,
                          first_name=user.first_name,
                          last_name=user.last_name,
                          type=user.type,
                          hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_loan(db: Session, loan_id: int):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()

def get_user_loans(db: Session, user_id):
    return db.query(models.Loan).filter(user_id == user_id).all()


def create_user_loan(db: Session, loan: schemas.LoanCreate, user_id: int):
    db_loan = models.Loan(**loan.dict(), user_id=user_id)
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan
