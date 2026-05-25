def test_register_student(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Jane Student",
            "email": "jane@school.com",
            "password": "securepass1",
            "role": "student",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jane@school.com"
    assert data["role"] == "student"
    assert data["is_active"] is True
    assert "hashed_password" not in data


def test_register_admin(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Admin User",
            "email": "admin@school.com",
            "password": "securepass1",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "admin"


def test_register_duplicate_email(client, student_user):
    response = client.post(
        "/auth/register",
        json={
            "name": "Another",
            "email": "student@test.com",
            "password": "securepass1",
            "role": "student",
        },
    )
    assert response.status_code == 409


def test_register_invalid_role(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Bad Role",
            "email": "bad@school.com",
            "password": "securepass1",
            "role": "teacher",
        },
    )
    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Short Pass",
            "email": "short@school.com",
            "password": "short",
            "role": "student",
        },
    )
    assert response.status_code == 422


def test_login_success(client, student_user):
    response = client.post(
        "/auth/login",
        json={"email": "student@test.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client, student_user):
    response = client.post(
        "/auth/login",
        json={"email": "student@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_inactive_user(client, inactive_user):
    response = client.post(
        "/auth/login",
        json={"email": "inactive@test.com", "password": "password123"},
    )
    assert response.status_code == 401
