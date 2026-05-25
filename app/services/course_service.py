from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.course_repository import CourseRepository
from app.schemas.course import CourseCreate, CourseUpdate


class CourseService:
    def __init__(self, db: Session):
        self.course_repo = CourseRepository(db)

    def list_active_courses(self):
        return self.course_repo.get_all_active()

    def get_course(self, course_id: int):
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")
        return course

    def create_course(self, data: CourseCreate):
        if self.course_repo.get_by_code(data.code):
            raise ConflictError("Course code already exists")
        return self.course_repo.create(title=data.title, code=data.code, capacity=data.capacity)

    def update_course(self, course_id: int, data: CourseUpdate):
        course = self.get_course(course_id)
        if data.code and data.code != course.code:
            existing = self.course_repo.get_by_code(data.code)
            if existing:
                raise ConflictError("Course code already exists")

        update_data = data.model_dump(exclude_unset=True)
        return self.course_repo.update(course, **update_data)

    def delete_course(self, course_id: int) -> None:
        course = self.get_course(course_id)
        self.course_repo.delete(course)

    def set_active_status(self, course_id: int, is_active: bool):
        course = self.get_course(course_id)
        return self.course_repo.update(course, is_active=is_active)
