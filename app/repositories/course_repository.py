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

    def create(self, title: str, code: str, capacity: int) -> Course:
        course = Course(title=title, code=code, capacity=capacity, is_active=True)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def update(self, course: Course, **kwargs) -> Course:
        # Callers pass only the fields they intend to change (the service uses
        # model_dump(exclude_unset=True)), so every provided kwarg is applied —
        # including explicit False/None values.
        for key, value in kwargs.items():
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
