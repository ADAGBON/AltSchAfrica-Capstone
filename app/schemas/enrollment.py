from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.course import CourseResponse
from app.schemas.user import UserResponse


class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnrollmentDetailResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    user: UserResponse
    course: CourseResponse

    model_config = ConfigDict(from_attributes=True)
