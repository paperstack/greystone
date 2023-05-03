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
    
    assert response.status_code == 200
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
    assert response.status_code == 200
    assert response.json() == {"id": 1, "term": 36, "interest_rate": 3.5, "amount": 20000, "loan_months": [{'id': 1, 'interest_amount': 100.0, 'month': 1, 'principal_amount': 200.0}], "users": []}

def test_create_new_loan_no_user(mocker, loan):
    mocker.patch("app.main.get_user_by_email", return_value=None)
    mocker.patch("app.main.create_loan", return_value=loan)
    response = client.post("/loans/test@test.com", json={"term": 36, "interest_rate": 3.5, "amount": 20000})
    assert response.status_code == 400
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
