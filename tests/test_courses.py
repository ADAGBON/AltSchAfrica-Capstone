from tests.conftest import auth_header


def _create_course(client, admin_headers, code="CS101", capacity=30):
    return client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "Intro to CS", "code": code, "capacity": capacity},
    )


def test_list_active_courses_public(client, db_session, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    _create_course(client, admin_headers, "ACTIVE1")
    inactive_id = _create_course(client, admin_headers, "INACTIVE1").json()["id"]
    client.patch(f"/courses/{inactive_id}/deactivate", headers=admin_headers)

    response = client.get("/courses")
    assert response.status_code == 200
    codes = [c["code"] for c in response.json()]
    assert "ACTIVE1" in codes
    assert "INACTIVE1" not in codes


def test_get_course_by_id_public(client, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    created = _create_course(client, admin_headers, "PUB101")
    course_id = created.json()["id"]

    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["code"] == "PUB101"


def test_get_course_not_found(client):
    response = client.get("/courses/9999")
    assert response.status_code == 404


def test_create_course_admin(client, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    response = _create_course(client, admin_headers, "ADM101")
    assert response.status_code == 201
    assert response.json()["capacity"] == 30


def test_create_course_student_forbidden(client, student_user):
    headers = auth_header(client, "student@test.com")
    response = client.post(
        "/courses",
        headers=headers,
        json={"title": "Hack", "code": "HACK", "capacity": 10},
    )
    assert response.status_code == 403


def test_create_course_duplicate_code(client, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    _create_course(client, admin_headers, "DUP101")
    response = _create_course(client, admin_headers, "DUP101")
    assert response.status_code == 409


def test_create_course_invalid_capacity(client, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    response = client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "Bad Cap", "code": "BAD1", "capacity": 0},
    )
    assert response.status_code == 422


def test_update_course_admin(client, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    course_id = _create_course(client, admin_headers, "UPD101").json()["id"]

    response = client.put(
        f"/courses/{course_id}",
        headers=admin_headers,
        json={"title": "Updated Title", "capacity": 50},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["capacity"] == 50


def test_activate_deactivate_course(client, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    course_id = _create_course(client, admin_headers, "ACT101").json()["id"]

    deactivate = client.patch(f"/courses/{course_id}/deactivate", headers=admin_headers)
    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False

    activate = client.patch(f"/courses/{course_id}/activate", headers=admin_headers)
    assert activate.status_code == 200
    assert activate.json()["is_active"] is True


def test_delete_course_admin(client, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    course_id = _create_course(client, admin_headers, "DEL101").json()["id"]

    response = client.delete(f"/courses/{course_id}", headers=admin_headers)
    assert response.status_code == 200
    assert client.get(f"/courses/{course_id}").status_code == 404
