from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError
from app.models.enrollment import Enrollment


class EnrollmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, enrollment_id: int) -> Enrollment | None:
        return (
            self.db.query(Enrollment)
            .options(joinedload(Enrollment.user), joinedload(Enrollment.course))
            .filter(Enrollment.id == enrollment_id)
            .first()
        )

    def get_by_user_and_course(self, user_id: int, course_id: int) -> Enrollment | None:
        return (
            self.db.query(Enrollment)
            .filter(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
            .first()
        )

    def get_all(self) -> list[Enrollment]:
        return (
            self.db.query(Enrollment)
            .options(joinedload(Enrollment.user), joinedload(Enrollment.course))
            .order_by(Enrollment.created_at.desc())
            .all()
        )

    def get_by_course_id(self, course_id: int) -> list[Enrollment]:
        return (
            self.db.query(Enrollment)
            .options(joinedload(Enrollment.user), joinedload(Enrollment.course))
            .filter(Enrollment.course_id == course_id)
            .order_by(Enrollment.created_at.desc())
            .all()
        )

    def create(self, user_id: int, course_id: int) -> Enrollment:
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        self.db.add(enrollment)
        try:
            self.db.commit()
        except IntegrityError:
            # The (user_id, course_id) unique constraint is the source of truth.
            # If a concurrent request enrolled the same student first, surface a
            # clean 409 instead of a 500.
            self.db.rollback()
            raise ConflictError("Already enrolled in this course")
        self.db.refresh(enrollment)
        return enrollment

    def delete(self, enrollment: Enrollment) -> None:
        self.db.delete(enrollment)
        self.db.commit()
