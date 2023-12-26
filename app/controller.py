from fastapi import HTTPException
from . import repo
import pandas as pd

def calculate_monthly_payment(amount, monthly_interest_rate, term):
    return ((amount * monthly_interest_rate * (1 + monthly_interest_rate)**term) /
            ((1 + monthly_interest_rate)**term - 1))

def generate_amortization_schedule(loan):
    # Unpack values from loan
    term = loan.loan_term
    amount = loan.amount
    annual_interest_rate = loan.annual_interest_rate / 100
    monthly_interest_rate = annual_interest_rate / 12

    monthly_payment = calculate_monthly_payment(amount, monthly_interest_rate, term)

    amortization_schedule = pd.DataFrame(columns = ['Month', 'Principal', 'Interest', 'Remaining balance'])
    remaining_principal = amount

    for month in range(1, term+1):
        monthly_interest_payment = (remaining_principal * annual_interest_rate) / 12
        monthly_principal_payment = monthly_payment - monthly_interest_payment
        remaining_principal -= monthly_principal_payment
        amortization_schedule.loc[len(amortization_schedule)] = [month, round(monthly_principal_payment, 2), round(monthly_interest_payment, 2), round(remaining_principal, 2)]
    amortization_schedule['Monthly payment'] = round(monthly_payment, 2)

    return amortization_schedule

def get_loan_schedule(db, loan_id):
    loan = repo.get_loan(db, loan_id)
    amortization_schedule = generate_amortization_schedule(loan)
    return amortization_schedule[['Month', 'Remaining balance', 'Monthly payment']].to_dict(orient='records')

def get_loan_summary(loan_id, month_num, db):
    loan = repo.get_loan(db, loan_id)
    if month_num < 1 or month_num > loan.loan_term:
        raise HTTPException(status_code=400, detail=f"Month number {month_num} is out of bounds")

    amortization_schedule = generate_amortization_schedule(loan)

    # compute summary values including current month
    current_balance = amortization_schedule[amortization_schedule['Month'] == month_num]['Remaining balance'].values[0]
    total_principal_paid = amortization_schedule[amortization_schedule['Month'] <= month_num]['Principal'].sum()
    total_interest_paid = amortization_schedule[amortization_schedule['Month'] <= month_num]['Interest'].sum()

    loan_summary = {
                    "Current principal balance": round(current_balance, 2),
                    "Total principal paid": round(total_principal_paid, 2),
                    "Total interest paid": round(total_interest_paid, 2)
                    }

    return loan_summary

def create_user_loan(db, loan, user_id):
    # in reality there is likely a higher minimmum but for mathematical purposes 1 month is minimum term
    if loan.loan_term < 1:
        raise HTTPException(status_code=400, detail="Term length must be at least 1 month")
    if loan.annual_interest_rate <= 0:
        raise HTTPException(status_code=400, detail="Interest rate must be greater than 0%")
    if loan.amount <= 0:
        raise HTTPException(status_code=400, detail="Loan amount must be greater than $0")
    return repo.create_user_loan(db=db, loan=loan, user_id=user_id)

def get_user_loans(db, user_id):
    user_loans = repo.get_user_loans(db, user_id)
    shared_loans = repo.get_loans_shared_with_user(db, user_id)
    return {"user's loans: ": user_loans, "loans shared with user: ": shared_loans}

def share_loan(db, loan_id, user_email):
    user = repo.get_user_by_email(db, user_email)
    if user is None:
        raise HTTPException(status_code=400, detail=f"User with email {user_email} does not exist")
        # potentially invite this user to app
    loan_viewer = repo.get_loan_viewer(db, loan_id, user.id)
    if loan_viewer:
        raise HTTPException(status_code=400, detail=f"Loan {loan_id} already shared with user {user_email}")
    return repo.create_loan_viewer(db, loan_id, user.id)
