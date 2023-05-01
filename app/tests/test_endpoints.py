from fastapi.testclient import TestClient
from app.main import app

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