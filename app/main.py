from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from . import controller, repo, models, schemas
from .database import engine, get_db
from .auth_handler import AuthHandler
from .validator import Validator

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_database_session():
    return next(get_db())

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/users/me")
def get_current_user(current_user: HTTPBasicCredentials = Depends(AuthHandler().authenticate_user)):
    return {"username": current_user.email, "first name": current_user.first_name, "last name": current_user.last_name}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_database_session)):
    db_user = repo.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail=f"Email {user.email} already registered")
    return repo.create_user(db=db, user=user)

@app.post("/users/{user_id}/loans", response_model=schemas.Loan)
def create_loan(loan: schemas.LoanCreate, user_id: int, db: Session = Depends(get_database_session), current_user: HTTPBasicCredentials = Depends(AuthHandler().authenticate_user)):
    user = AuthHandler().check_existing_user(db, user_id)
    if current_user.id == user_id or user.type == 'broker':
        return controller.create_user_loan(db=db, loan=loan, user_id=user_id)
    raise HTTPException(status_code=401, detail=f"User with id {current_user.id} is not authorized to create new loan for user {user_id}")

@app.get("/users/{user_id}/loans")
def get_user_loans(user_id: int, db: Session = Depends(get_database_session), current_user: HTTPBasicCredentials = Depends(AuthHandler().authenticate_user)):
    user = AuthHandler().check_existing_user(db, user_id)
    # user can see their own loans and broker can see all loans
    if current_user.id == user_id or user.type == 'broker':
        return controller.get_user_loans(db, user_id)
    raise HTTPException(status_code=401, detail=f"User with id {current_user.id} is not authorized to view loans for user {user_id}")

@app.get("/users/{user_id}/loans/{loan_id}/schedule")
def get_loan_schedule(user_id: int, loan_id: int, db: Session = Depends(get_database_session), current_user: HTTPBasicCredentials = Depends(AuthHandler().authenticate_user)):
    user = AuthHandler().check_existing_user(db, user_id)
    loan = Validator().check_existing_loan(db, loan_id)
    AuthHandler().check_user_page(current_user.id, user_id)
    # user can see their own loans and loans shard with them, broker can see all loans
    loan_viewer = repo.get_loan_viewer(db, loan_id, user_id)
    if loan and (loan.user_id == current_user.id or loan_viewer or user.type == 'broker'):
        return controller.get_loan_schedule(db, loan_id)
    raise HTTPException(status_code=401, detail=f"User with id {current_user.id} is not authorized to access loan with id {loan_id}")

@app.get("/users/{user_id}/loans/{loan_id}/summary/{month_num}")
def get_loan_summary(user_id: int, loan_id: int, month_num: int, db: Session = Depends(get_database_session), current_user: HTTPBasicCredentials = Depends(AuthHandler().authenticate_user)):
    user = AuthHandler().check_existing_user(db, user_id)
    loan = Validator().check_existing_loan(db, loan_id)
    AuthHandler().check_user_page(current_user.id, user_id)
    # user can see their own loans and loans shard with them, broker can see all loans
    loan_viewer = repo.get_loan_viewer(db, loan_id, user_id)
    if loan and (loan.user_id == user.id or loan_viewer or user.type == 'broker'):
        return controller.get_loan_summary(loan_id, month_num, db)
    raise HTTPException(status_code=401, detail=f"User with id {current_user.id} is not authorized to access loan with id {loan_id}")


@app.post("/users/{user_id}/loans/{loan_id}/share", response_model=schemas.LoanViewer)
def share_loan(loan_viewer: schemas.LoanViewerCreate, user_id: int, loan_id: int, db: Session = Depends(get_database_session), current_user: HTTPBasicCredentials = Depends(AuthHandler().authenticate_user)):
    user = AuthHandler().check_existing_user(db, user_id)
    loan = Validator().check_existing_loan(db, loan_id)
    AuthHandler().check_user_page(current_user.id, user_id)
    # this could be a warning or log rather than an exception
    if loan_viewer.user_email == current_user.email:
        raise HTTPException(status_code=401, detail=f"Loan does not need to be shared with ones own email")
    # only user can share their own loans
    if loan and loan.user_id == user.id:
        return controller.share_loan(db, loan_id, loan_viewer.user_email)
    raise HTTPException(status_code=401, detail=f"User with id {current_user.id} is not authorized to share loan with id {loan_id}")
