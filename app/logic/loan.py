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
    """
    Generate the loan schedule by iterating through all the loan months, running down the balance,
    and capturing the record for each month in a list. 
    NOTE: The remaining balance is calculated as post-payment for a given month (ie 1k loan w/ 100 principal payment 
    amount at month 1 will have a remaining balance of 900, and all loans should have a 0 remaining balance on the final month)
    """
    
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

def get_month_summary(db: Session, loan_id: int, month: int):
    """
    Get the loan summary at a given month by iterating through all the months,
    summing the paid totals, and running down the balance. We can break out of the
    loop once we've found the requested month. If we make it all the way through
    it means the requested month is outside the bounds of the payout schedule and we'll
    use a "None" principal balance to signal that the requested month was not found to the caller.
    """
    
    result = None
    loan: Loan = db.get(Loan, loan_id)
    if loan:
        principal_paid = Decimal(0)
        interest_paid = Decimal(0)
        principal_balance = None
        remaining_balance = Decimal(loan.amount)
        for loan_month in loan.loan_months:
            principal_paid += loan_month.principal_amount
            interest_paid += loan_month.interest_amount
            remaining_balance -= loan_month.principal_amount
            if loan_month.month == month:
                principal_balance = remaining_balance
                break
        result = {"principal_balance": principal_balance, "principal_paid": principal_paid, "interest_paid": interest_paid}
    return result

def _create_amoritization_schedule(loan:Loan):
    result = []
    payout_schedule = generate_amoritization_schedule(interest=loan.interest_rate, term=loan.term, principal=loan.amount)
    
    for month, payout in enumerate(payout_schedule):
        loan_month = LoanMonth(month=month+1, principal_amount=payout[0], interest_amount=payout[1])
        result.append(loan_month)
            
    return result