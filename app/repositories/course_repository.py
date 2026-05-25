from sqlalchemy.orm import Session

from app.models.course import Course


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, course_id: int) -> Course | None:
        return self.db.query(Course).filter(Course.id == course_id).first()

    def get_by_code(self, code: str) -> Course | None:
        return self.db.query(Course).filter(Course.code == code).first()

    def get_all_active(self) -> list[Course]:
        return self.db.query(Course).filter(Course.is_active.is_(True)).all()

    def get_all(self) -> list[Course]:
        return self.db.query(Course).all()

    def create(self, title: str, code: str, capacity: int) -> Course:
        course = Course(title=title, code=code, capacity=capacity, is_active=True)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def update(self, course: Course, **kwargs) -> Course:
        for key, value in kwargs.items():
            if value is not None:
                setattr(course, key, value)
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete(self, course: Course) -> None:
        self.db.delete(course)
        self.db.commit()

    def count_enrollments(self, course_id: int) -> int:
        from app.models.enrollment import Enrollment

        return self.db.query(Enrollment).filter(Enrollment.course_id == course_id).count()
