from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserLogin, UserRegister


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def register(self, data: UserRegister):
        if self.user_repo.get_by_email(data.email):
            raise ConflictError("Email already registered")

        # Public registration always creates a student. Never trust a
        # client-supplied role here — admins are seeded out-of-band.
        user = self.user_repo.create(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
            role=UserRole.student,
        )
        return user

    def login(self, data: UserLogin) -> str:
        user = self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Account is inactive")

        return create_access_token(str(user.id))
