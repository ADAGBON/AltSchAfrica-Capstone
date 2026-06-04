"""Create an admin user from environment variables.

Admins cannot be created through the public /auth/register endpoint (that would
be a privilege-escalation hole). Use this script instead, e.g.:

    ADMIN_NAME="Site Admin" \\
    ADMIN_EMAIL="admin@example.com" \\
    ADMIN_PASSWORD="a-long-strong-password" \\
    python -m scripts.seed_admin

Running it again with the same email is a no-op (idempotent).
"""
import os
import sys

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


def main() -> int:
    name = os.environ.get("ADMIN_NAME", "Admin")
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")

    if not email or not password:
        print("ERROR: ADMIN_EMAIL and ADMIN_PASSWORD must be set.", file=sys.stderr)
        return 1
    if len(password) < 8:
        print("ERROR: ADMIN_PASSWORD must be at least 8 characters.", file=sys.stderr)
        return 1

    db = SessionLocal()
    try:
        repo = UserRepository(db)
        existing = repo.get_by_email(email)
        if existing:
            if existing.role != UserRole.admin:
                existing.role = UserRole.admin
                db.commit()
                print(f"Promoted existing user {email} to admin.")
            else:
                print(f"Admin {email} already exists. Nothing to do.")
            return 0

        user = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.admin,
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"Created admin {email}.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
