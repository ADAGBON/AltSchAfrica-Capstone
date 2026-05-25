from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.database import get_db
from app.dependencies import get_current_user, require_admin, require_student
from app.models.user import User
from app.core.http_utils import raise_http_exception
from app.schemas.common import MessageResponse
from app.schemas.enrollment import EnrollmentCreate, EnrollmentDetailResponse, EnrollmentResponse
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    data: EnrollmentCreate,
    current_user: Annotated[User, Depends(require_student)],
    db: Session = Depends(get_db),
):
    try:
        return EnrollmentService(db).enroll_student(current_user, data.course_id)
    except AppException as exc:
        raise_http_exception(exc)


@router.delete("/course/{course_id}", response_model=MessageResponse)
def deregister_from_course(
    course_id: int,
    current_user: Annotated[User, Depends(require_student)],
    db: Session = Depends(get_db),
):
    try:
        EnrollmentService(db).deregister_student(current_user, course_id)
        return MessageResponse(message="Successfully deregistered from course")
    except AppException as exc:
        raise_http_exception(exc)


@router.get("", response_model=list[EnrollmentDetailResponse])
def list_all_enrollments(
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    return EnrollmentService(db).list_all_enrollments()


@router.get("/course/{course_id}", response_model=list[EnrollmentDetailResponse])
def list_course_enrollments(
    course_id: int,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    try:
        return EnrollmentService(db).list_enrollments_by_course(course_id)
    except AppException as exc:
        raise_http_exception(exc)


@router.delete("/{enrollment_id}", response_model=MessageResponse)
def admin_remove_enrollment(
    enrollment_id: int,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    try:
        EnrollmentService(db).admin_remove_enrollment(enrollment_id)
        return MessageResponse(message="Enrollment removed successfully")
    except AppException as exc:
        raise_http_exception(exc)
