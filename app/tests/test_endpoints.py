from fastapi.testclient import TestClient
from app.main import app
from app.models import User

client  = TestClient(app)

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
    
def test_create_new_user(mocker):
    user = User(id=1,first_name="Grey", last_name="Stone", email="test@test.com")
    mocker.patch("app.main.get_user_by_email", return_value=None)
    mocker.patch("app.main.create_user", return_value=user)
    response = client.post("/users/", json={"first_name":"Grey", "last_name": "Stone", "email":"test@test.com"})
    
    assert response.status_code == 200
    assert response.json() == {'email': 'test@test.com', 'first_name': 'Grey', 'id': 1, 'last_name': 'Stone'}
    
def test_create_new_user_email_exists(mocker):
    user = User(first_name="Grey", last_name="Stone")
    mocker.patch("app.main.get_user_by_email", return_value=user)
    response = client.post("/users/", json={"first_name":"Grey", "last_name": "Stone", "email":"test@test.com"})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Email already registered'}