from sqlalchemy.orm.session import Session
from app import schemas
from app.models import User, Loan, LoanMonth
from app.logic.common import generate_amoritization_schedule


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

def _create_amoritization_schedule(loan:Loan):
    result = []
    payout_schedule = generate_amoritization_schedule(interest=loan.interest_rate, term=loan.term, principal=loan.amount)
    
    for month, payout in enumerate(payout_schedule):
        loan_month = LoanMonth(month=month+1, principal_amount=payout[0], interest_amount=payout[1])
        result.append(loan_month)
            
    return result