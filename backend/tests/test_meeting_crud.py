from fastapi.testclient import TestClient

from backend.app.main import app


def test_meeting_list_and_health():
    client = TestClient(app)
    response = client.get('/meetings')
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
