from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if not credentials:
        raise UnauthorizedError("Not authenticated")

    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        raise UnauthorizedError("Invalid or expired token")

    user = UserRepository(db).get_by_id(int(user_id))
    if not user:
        raise UnauthorizedError("User not found")

    if not user.is_active:
        raise UnauthorizedError("Account is inactive")

    return user


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.admin:
        raise ForbiddenError("Admin access required")
    return current_user


def require_student(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.student:
        raise ForbiddenError("Student access required")
    return current_user
