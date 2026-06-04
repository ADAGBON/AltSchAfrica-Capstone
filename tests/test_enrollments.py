from tests.conftest import auth_header


def _setup_course(client, admin_headers, code="ENR101", capacity=2):
    return client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "Enrollment Course", "code": code, "capacity": capacity},
    ).json()["id"]


def test_enroll_student_success(client, student_user, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    student_headers = auth_header(client, "student@test.com")
    course_id = _setup_course(client, admin_headers)

    response = client.post(
        "/enrollments",
        headers=student_headers,
        json={"course_id": course_id},
    )
    assert response.status_code == 201
    assert response.json()["course_id"] == course_id


def test_enroll_duplicate_fails(client, student_user, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    student_headers = auth_header(client, "student@test.com")
    course_id = _setup_course(client, admin_headers, "DUP201")

    client.post("/enrollments", headers=student_headers, json={"course_id": course_id})
    response = client.post(
        "/enrollments",
        headers=student_headers,
        json={"course_id": course_id},
    )
    assert response.status_code == 409


def test_enroll_full_course_fails(client, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    course_id = _setup_course(client, admin_headers, "FULL01", capacity=1)

    client.post(
        "/auth/register",
        json={
            "name": "Student A",
            "email": "a@test.com",
            "password": "password123",
        },
    )
    client.post(
        "/auth/register",
        json={
            "name": "Student B",
            "email": "b@test.com",
            "password": "password123",
        },
    )

    headers_a = auth_header(client, "a@test.com")
    headers_b = auth_header(client, "b@test.com")

    client.post("/enrollments", headers=headers_a, json={"course_id": course_id})
    response = client.post("/enrollments", headers=headers_b, json={"course_id": course_id})
    assert response.status_code == 409


def test_enroll_inactive_course_fails(client, student_user, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    student_headers = auth_header(client, "student@test.com")
    course_id = _setup_course(client, admin_headers, "INACT1")
    client.patch(f"/courses/{course_id}/deactivate", headers=admin_headers)

    response = client.post(
        "/enrollments",
        headers=student_headers,
        json={"course_id": course_id},
    )
    assert response.status_code == 409


def test_admin_cannot_enroll(client, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    course_id = _setup_course(client, admin_headers, "ADMENR")

    response = client.post(
        "/enrollments",
        headers=admin_headers,
        json={"course_id": course_id},
    )
    assert response.status_code == 403


def test_deregister_student(client, student_user, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    student_headers = auth_header(client, "student@test.com")
    course_id = _setup_course(client, admin_headers, "DEREG1")

    client.post("/enrollments", headers=student_headers, json={"course_id": course_id})
    response = client.delete(f"/enrollments/course/{course_id}", headers=student_headers)
    assert response.status_code == 200


def test_deregister_not_enrolled(client, student_user, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    student_headers = auth_header(client, "student@test.com")
    course_id = _setup_course(client, admin_headers, "DEREG2")

    response = client.delete(f"/enrollments/course/{course_id}", headers=student_headers)
    assert response.status_code == 404


def test_list_all_enrollments_admin(client, student_user, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    student_headers = auth_header(client, "student@test.com")
    course_id = _setup_course(client, admin_headers, "LIST01")

    client.post("/enrollments", headers=student_headers, json={"course_id": course_id})
    response = client.get("/enrollments", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_list_enrollments_student_forbidden(client, student_user):
    headers = auth_header(client, "student@test.com")
    response = client.get("/enrollments", headers=headers)
    assert response.status_code == 403


def test_list_enrollments_by_course(client, student_user, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    student_headers = auth_header(client, "student@test.com")
    course_id = _setup_course(client, admin_headers, "BYCRS1")

    client.post("/enrollments", headers=student_headers, json={"course_id": course_id})
    response = client.get(f"/enrollments/course/{course_id}", headers=admin_headers)
    assert response.status_code == 200
    assert all(e["course_id"] == course_id for e in response.json())


def test_admin_remove_enrollment(client, student_user, admin_user):
    admin_headers = auth_header(client, "admin@test.com")
    student_headers = auth_header(client, "student@test.com")
    course_id = _setup_course(client, admin_headers, "RMV01")

    enrollment = client.post(
        "/enrollments",
        headers=student_headers,
        json={"course_id": course_id},
    ).json()

    response = client.delete(
        f"/enrollments/{enrollment['id']}",
        headers=admin_headers,
    )
    assert response.status_code == 200
