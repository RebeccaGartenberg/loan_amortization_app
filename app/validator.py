from fastapi import HTTPException
from .database import get_db
from . import repo

class Validator:
    def __init__(self):
        self.db = next(get_db())

    def check_existing_loan(self, db, loan_id):
        loan = repo.get_loan(db, loan_id)
        if not loan:
            raise HTTPException(status_code=404, detail=f"Loan with id {loan_id} does not exist")
        return loan
