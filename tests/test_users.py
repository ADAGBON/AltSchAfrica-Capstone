from tests.conftest import auth_header


def test_get_profile_authenticated(client, student_user):
    headers = auth_header(client, "student@test.com")
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student@test.com"
    assert data["name"] == "Test Student"


def test_get_profile_unauthenticated(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_profile_invalid_token(client):
    response = client.get("/users/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
