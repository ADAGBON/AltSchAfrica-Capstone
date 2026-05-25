from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.core.http_utils import raise_http_exception
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        return UserService(db).get_profile(current_user.id)
    except AppException as exc:
        raise_http_exception(exc)
