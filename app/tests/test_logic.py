import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from app.logic.ping_db import ping_db
from app.schemas import UserCreate, LoanCreate
from app.logic.user import create_user, get_user_loans
from app.models import User, LoanMonth, Loan
from app.logic.loan import create_loan, get_loan_schedule, get_month_summary,\
    share_loan
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
   
@pytest.fixture(scope="module")
def user():
    user = User(email='test@test.com', first_name="Test", last_name="McTest")
    return user

@pytest.fixture(scope="module")
def user_2():
    user = User(email='test2@test.com', first_name="Test", last_name="McTest")
    return user

@pytest.fixture(scope="module")
def user_loans():
    loan = Loan(term=36, interest_rate=3.5, amount=300)
    loan.loan_months.append(LoanMonth(month=1, principal_amount=100, interest_amount=200))
    loan.loan_months.append(LoanMonth(month=2, principal_amount=200, interest_amount=100))

    loan_2 = Loan(term=48, interest_rate=2.5, amount=500)
    loan_2.loan_months.append(LoanMonth(month=1, principal_amount=200, interest_amount=300))
    loan_2.loan_months.append(LoanMonth(month=2, principal_amount=300, interest_amount=200))

    user = User(email='test@test.com', first_name="Test", last_name="McTest", loans=[loan, loan_2])
    return user

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

def test_get_month_summary_for_first_month(db, loan):
    db.add(loan)
    db.commit()
    db.refresh(loan)
    month_summary = get_month_summary(db=db, loan_id=loan.id, month=1)
    assert month_summary["principal_balance"] == 200
    assert month_summary["principal_paid"] == 100
    assert month_summary["interest_paid"] == 200

def test_get_month_summary_for_last_month(db, loan):
    db.add(loan)
    db.commit()
    db.refresh(loan)
    month_summary = get_month_summary(db=db, loan_id=loan.id, month=2)
    assert month_summary["principal_balance"] == 0
    assert month_summary["principal_paid"] == 300
    assert month_summary["interest_paid"] == 300

def test_get_month_summary_no_loan(db, loan):
    db.add(loan)
    db.commit()
    db.refresh(loan)
    month_summary = get_month_summary(db=db, loan_id=loan.id + 1, month=1)
    assert month_summary is None

def test_get_month_summary_no_month(db, loan):
    db.add(loan)
    db.commit()
    db.refresh(loan)
    month_summary = get_month_summary(db=db, loan_id=loan.id, month=3)
    assert month_summary["principal_balance"] is None

def test_get_user_loans(db, user_loans):
    db.add(user_loans)
    db.commit()
    db.refresh(user_loans)
    loans = get_user_loans(db=db, user=user_loans)
    assert len(loans) == 2
    assert loans[0] != loans[1]

def test_share_loan(db, user, user_2, loan):
    loan.users.append(user)
    db.add(loan)
    db.add(user_2)
    db.commit()
    db.refresh(loan)
    db.refresh(user)
    db.refresh(user_2)

    # Starting state sanity check
    assert len(loan.users) == 1
    assert loan.users[0] == user
    
    share_loan(db, loan, user_2)
    
    assert len(loan.users) == 2
    assert loan.users[0] != loan.users[1]
    