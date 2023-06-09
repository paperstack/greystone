from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Loan, LoanMonth
import pytest

client  = TestClient(app)

@pytest.fixture(scope="module")
def user():
    user = User(id=1,first_name="Grey", last_name="Stone", email="test@test.com")
    return user

@pytest.fixture(scope="module")
def loan():
    loan = Loan(id=1, term=36, interest_rate=3.5, amount=20000)
    loan.loan_months.append(LoanMonth(id=1, month=1, principal_amount=200, interest_amount=100))
    return loan

@pytest.fixture(scope="module")
def loan_2():
    loan = Loan(id=2, term=48, interest_rate=2.5, amount=30000)
    loan.loan_months.append(LoanMonth(id=2, month=1, principal_amount=300, interest_amount=200))
    return loan

@pytest.fixture(scope="module")
def loan_schedule():
    result = []
    result.append({"month": 1, "remaining_balance": 300, "monthly_payment": 100})
    result.append({"month": 2, "remaining_balance": 200, "monthly_payment": 100})
    return result

def test_health_check_ok(mocker):
    mocker.patch("app.main.ping_db", return_value=True)
    response = client.get("/health_check")
    assert response.status_code == 200
    assert response.json() == {"Status": "Ok"}
    
def test_health_check_no_db(mocker):
    mocker.patch("app.main.ping_db", return_value=False)
    response = client.get("/health_check")
    assert response.status_code == 400
    assert response.json() == {'detail': 'No Database Connection'}
    
def test_create_new_user(mocker, user):
    mocker.patch("app.main.get_user_by_email", return_value=None)
    mocker.patch("app.main.create_user", return_value=user)
    response = client.post("/users/", json={"first_name":"Grey", "last_name": "Stone", "email":"test@test.com"})
    
    assert response.status_code == 201
    assert response.json() == {'email': 'test@test.com', 'first_name': 'Grey', 'id': 1, 'last_name': 'Stone', "loans": []}
    
def test_create_new_user_email_exists(mocker, user):
    mocker.patch("app.main.get_user_by_email", return_value=user)
    response = client.post("/users/", json={"first_name":"Grey", "last_name": "Stone", "email":"test@test.com"})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Email already registered'}
    
def test_create_new_loan(mocker, user, loan):
    mocker.patch("app.main.get_user_by_email", return_value=user)
    mocker.patch("app.main.create_loan", return_value=loan)
    response = client.post("/loans/test@test.com", json={"term": 36, "interest_rate": 3.5, "amount": 20000})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "term": 36, "interest_rate": 3.5, "amount": 20000, "loan_months": [{'id': 1, 'interest_amount': 100.0, 'month': 1, 'principal_amount': 200.0}], "users": []}

def test_create_new_loan_no_user(mocker, loan):
    mocker.patch("app.main.get_user_by_email", return_value=None)
    mocker.patch("app.main.create_loan", return_value=loan)
    response = client.post("/loans/test@test.com", json={"term": 36, "interest_rate": 3.5, "amount": 20000})
    assert response.status_code == 404
    assert response.json() == {'detail': 'No user for loan found'}

def test_create_new_loan_bad_data(mocker, user, loan):
    mocker.patch("app.main.get_user_by_email", return_value=user)
    mocker.patch("app.main.create_loan", return_value=loan)
    #TODO: check message bodies
    response = client.post("/loans/test@test.com", json={"term": -1, "interest_rate": 3.5, "amount": 20000})
    assert response.status_code == 422
    response = client.post("/loans/test@test.com", json={"term": 10, "interest_rate": -1, "amount": 20000})
    assert response.status_code == 422
    response = client.post("/loans/test@test.com", json={"term": 10, "interest_rate": 3.5, "amount": -20000})
    assert response.status_code == 422

def test_fetch_loan_schedule(mocker, loan_schedule):
    mocker.patch("app.main.get_loan_schedule", return_value=loan_schedule)
    response = client.get("/loans/1/schedule")
    assert response.status_code == 200
    assert response.json() == [{"month": 1, "remaining_balance": 300, "monthly_payment": 100},
                               {"month": 2, "remaining_balance": 200, "monthly_payment": 100}]

def test_fetch_loan_schedule_no_loan(mocker):
    mocker.patch("app.main.get_loan_schedule", return_value=None)
    response = client.get("/loans/1/schedule")
    assert response.status_code == 404
    assert response.json() == {"detail": "Loan not found"}

def test_fetch_month_summary(mocker):
    month_summary = {"principal_balance": 1000, "principal_paid": 900, "interest_paid": 800}
    mocker.patch("app.main.get_month_summary", return_value=month_summary)
    response = client.get("/loans/1/month/1/")
    assert response.status_code == 200
    assert response.json() == month_summary

def test_fetch_month_summary_no_loan(mocker):
    month_summary = None
    mocker.patch("app.main.get_month_summary", return_value=month_summary)
    response = client.get("/loans/1/month/1/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Loan not found"}
    
def test_fetch_month_summary_no_month(mocker):
    month_summary = {"principal_balance": None, "principal_paid": 900, "interest_paid": 800}
    mocker.patch("app.main.get_month_summary", return_value=month_summary)
    response = client.get("/loans/1/month/1/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Requested month not found"}    

def test_user_loans(mocker, user, loan, loan_2):
    mocker.patch("app.main.get_user_by_email", return_value=user)
    mocker.patch("app.main.get_user_loans", return_value=[loan, loan_2])
    response = client.get("/users/test@test.com/loans/")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "term": 36, "interest_rate": 3.5, "amount": 20000, "loan_months": [{'id': 1, 'interest_amount': 100.0, 'month': 1, 'principal_amount': 200.0}]},
                               {"id": 2, "term": 48, "interest_rate": 2.5, "amount": 30000, "loan_months": [{'id': 2, 'interest_amount': 200.0, 'month': 1, 'principal_amount': 300.0}]}]

def test_user_loans_no_user(mocker, loan, loan_2):
    mocker.patch("app.main.get_user_by_email", return_value=None)
    mocker.patch("app.main.get_user_loans", return_value=[loan, loan_2])
    response = client.get("/users/test@test.com/loans/")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}    

def test_share_loan(mocker, user, loan):
    mocker.patch("app.main.get_user_by_email", return_value=user)
    mocker.patch("app.main.get_loan", return_value=loan)
    mocker.patch("app.main.share_loan", return_value=None)
    response = client.patch("/loans/1/share/test@test.com/")
    assert response.status_code == 200

def test_share_loan_no_user(mocker, loan):
    mocker.patch("app.main.get_user_by_email", return_value=None)
    mocker.patch("app.main.get_loan", return_value=loan)
    mocker.patch("app.main.share_loan", return_value=None)
    response = client.patch("/loans/1/share/test@test.com/")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}    

def test_share_loan_no_loan(mocker, user):
    mocker.patch("app.main.get_user_by_email", return_value=user)
    mocker.patch("app.main.get_loan", return_value=None)
    mocker.patch("app.main.share_loan", return_value=None)
    response = client.patch("/loans/1/share/test@test.com/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Loan not found"}    
