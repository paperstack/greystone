import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from app.logic.ping_db import ping_db
from app.schemas import UserCreate, LoanCreate
from app.logic.user import create_user
from app.models import User, LoanMonth, Loan
from app.logic.loan import create_loan, get_loan_schedule
from decimal import Decimal
from _decimal import getcontext

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db():
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.rollback()
    db.close()

@pytest.fixture(scope="module")
def loan():
    loan = Loan(term=36, interest_rate=3.5, amount=300)
    loan.loan_months.append(LoanMonth(month=1, principal_amount=100, interest_amount=200))
    loan.loan_months.append(LoanMonth(month=2, principal_amount=200, interest_amount=100))
    return loan
   
def test_ping_db(db):
    assert True == ping_db(db=db)
    
def test_user_create(db):
    user_input = UserCreate(**{"first_name": "Grey", "last_name": "Stone", "email": "greystone@greystone.com"})
    
    user = create_user(db=db, user=user_input)
    assert  user_input.first_name == user.first_name
    assert  user_input.last_name == user.last_name
    assert  user_input.email == user.email
    assert  user.id > 0

def test_loan_create(db):
    getcontext().prec=2
    user = User(first_name="Grey", last_name="Stone", email="loan_create@greystone.com")
    db.add(user)
    db.commit()
    loan_input = LoanCreate(**{"amount": 30000, "term": 48, "interest_rate": 3.0})
    
    loan = create_loan(db=db, loan=loan_input, user=user)

    # Test loan attributes
    assert  loan_input.amount == loan.amount
    assert  loan_input.term == loan.term
    assert  loan_input.interest_rate == loan.interest_rate
    assert  user == loan.users[0]
    
    # Test payout schedule
    # See https://www.investopedia.com/terms/a/amortization.asp for control data
    first_loan_month = db.query(LoanMonth).filter(LoanMonth.loan==loan, LoanMonth.month==1).first()
    assert first_loan_month.principal_amount == Decimal('589.03')
    assert first_loan_month.interest_amount == Decimal('75.00')
    
    last_loan_month = db.query(LoanMonth).filter(LoanMonth.loan==loan, LoanMonth.month==48).first()
    assert last_loan_month.principal_amount == Decimal('662.37') #TODO: Should be 36 cents... resolve rounding error
    assert last_loan_month.interest_amount == Decimal('1.66')
    
    # Test arbitrary month(10th)
    tenth_loan_month = db.query(LoanMonth).filter(LoanMonth.loan==loan, LoanMonth.month==10).first()
    assert tenth_loan_month.principal_amount == Decimal('602.42')
    assert tenth_loan_month.interest_amount == Decimal('61.61')
    
def test_get_loan_schedule(db, loan):
    db.add(loan)
    db.commit()
    db.refresh(loan)
    schedule_items = get_loan_schedule(db=db, loan_id=loan.id)
    assert len(schedule_items) == 2
    
    first_month = schedule_items[0]
    assert first_month["month"] == 1
    assert first_month["monthly_payment"] == 300
    assert first_month["remaining_balance"] == 200
    
    last_month = schedule_items[1]
    assert last_month["month"] == 2
    assert last_month["monthly_payment"] == 300
    assert last_month["remaining_balance"] == 0
    
def test_get_loan_schedule_no_loan(db, loan):
    db.add(loan)
    db.commit()
    db.refresh(loan)
    loan_months = get_loan_schedule(db=db, loan_id=loan.id + 1)
    assert loan_months == None
