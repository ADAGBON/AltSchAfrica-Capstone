from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=list[CourseResponse])
def list_active_courses(db: Session = Depends(get_db)):
    return CourseService(db).list_active_courses()


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    return CourseService(db).get_course(course_id)


@router.post("", response_model=CourseResponse, status_code=201)
def create_course(
    data: CourseCreate,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    return CourseService(db).create_course(data)


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    data: CourseUpdate,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    return CourseService(db).update_course(course_id, data)


@router.patch("/{course_id}/activate", response_model=CourseResponse)
def activate_course(
    course_id: int,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    return CourseService(db).set_active_status(course_id, is_active=True)


@router.patch("/{course_id}/deactivate", response_model=CourseResponse)
def deactivate_course(
    course_id: int,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    return CourseService(db).set_active_status(course_id, is_active=False)


@router.delete("/{course_id}", response_model=MessageResponse)
def delete_course(
    course_id: int,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    CourseService(db).delete_course(course_id)
    return MessageResponse(message="Course deleted successfully")
