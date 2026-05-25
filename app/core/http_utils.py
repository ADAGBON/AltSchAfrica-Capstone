from fastapi import HTTPException

from app.core.exceptions import AppException


def raise_http_exception(exc: AppException):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)
