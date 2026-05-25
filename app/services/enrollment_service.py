from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.user import User, UserRole
from app.repositories.course_repository import CourseRepository
from app.repositories.enrollment_repository import EnrollmentRepository


class EnrollmentService:
    def __init__(self, db: Session):
        self.enrollment_repo = EnrollmentRepository(db)
        self.course_repo = CourseRepository(db)

    def enroll_student(self, user: User, course_id: int):
        if user.role != UserRole.student:
            raise ForbiddenError("Only students can enroll in courses")

        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")

        if not course.is_active:
            raise ConflictError("Cannot enroll in an inactive course")

        if self.enrollment_repo.get_by_user_and_course(user.id, course_id):
            raise ConflictError("Already enrolled in this course")

        enrolled_count = self.course_repo.count_enrollments(course_id)
        if enrolled_count >= course.capacity:
            raise ConflictError("Course is full")

        return self.enrollment_repo.create(user_id=user.id, course_id=course_id)

    def deregister_student(self, user: User, course_id: int) -> None:
        if user.role != UserRole.student:
            raise ForbiddenError("Only students can deregister from courses")

        enrollment = self.enrollment_repo.get_by_user_and_course(user.id, course_id)
        if not enrollment:
            raise NotFoundError("Enrollment not found")

        self.enrollment_repo.delete(enrollment)

    def list_all_enrollments(self):
        return self.enrollment_repo.get_all()

    def list_enrollments_by_course(self, course_id: int):
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")
        return self.enrollment_repo.get_by_course_id(course_id)

    def admin_remove_enrollment(self, enrollment_id: int) -> None:
        enrollment = self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise NotFoundError("Enrollment not found")
        self.enrollment_repo.delete(enrollment)
