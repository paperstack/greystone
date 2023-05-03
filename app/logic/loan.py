from sqlalchemy.orm.session import Session
from app import schemas
from app.models import User, Loan, LoanMonth
from app.logic.common import generate_amoritization_schedule
from decimal import Decimal


def create_loan(db: Session, loan: schemas.LoanCreate, user: User):
    """
    Creates a loan for a given user with a respective payout schedule
    """
    _loan = Loan(**loan.dict(), users=[user])
    _loan.loan_months = _create_amoritization_schedule(_loan)
    db.add(_loan)
    db.commit()
    db.refresh(_loan)
    return _loan

def get_loan_schedule(db: Session, loan_id: int):
    result = None
    loan: Loan = db.get(Loan, loan_id)
    if loan:
        result = []
        remaining_balance = Decimal(loan.amount)
        for loan_month in loan.loan_months:
            remaining_balance -= loan_month.principal_amount
            monthly_payment = loan_month.principal_amount + loan_month.interest_amount
            result.append({"month": loan_month.month, "remaining_balance": remaining_balance, "monthly_payment": monthly_payment})
    return result

def _create_amoritization_schedule(loan:Loan):
    result = []
    payout_schedule = generate_amoritization_schedule(interest=loan.interest_rate, term=loan.term, principal=loan.amount)
    
    for month, payout in enumerate(payout_schedule):
        loan_month = LoanMonth(month=month+1, principal_amount=payout[0], interest_amount=payout[1])
        result.append(loan_month)
            
    return result