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

def get_loan_schedule(loan_id, db):
    loan = repo.get_loan(db, loan_id)
    amortization_schedule = generate_amortization_schedule(loan)
    return amortization_schedule[['Month', 'Remaining balance', 'Monthly payment']].to_dict(orient='records')

def get_loan_summary(loan_id, month_num, db):
    loan = repo.get_loan(db, loan_id)
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
