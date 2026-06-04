def test_register_student(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Jane Student",
            "email": "jane@school.com",
            "password": "securepass1",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jane@school.com"
    assert data["role"] == "student"
    assert data["is_active"] is True
    assert "hashed_password" not in data


def test_register_always_creates_student(client):
    # Even if a caller tries to smuggle in an elevated role, the public
    # endpoint must reject the unknown field and never create an admin.
    response = client.post(
        "/auth/register",
        json={
            "name": "Sneaky",
            "email": "sneaky@school.com",
            "password": "securepass1",
            "role": "admin",
        },
    )
    assert response.status_code == 422


def test_register_duplicate_email(client, student_user):
    response = client.post(
        "/auth/register",
        json={
            "name": "Another",
            "email": "student@test.com",
            "password": "securepass1",
        },
    )
    assert response.status_code == 409


def test_register_missing_name(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "noname@school.com",
            "password": "securepass1",
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
