from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.routers import auth, courses, enrollments, users

app = FastAPI(
    title="Course Enrollment Platform API",
    description="A secure RESTful API for managing course enrollments with JWT auth and RBAC.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    messages = []
    for error in errors:
        loc = " -> ".join(str(item) for item in error.get("loc", []))
        messages.append(f"{loc}: {error.get('msg')}")
    return JSONResponse(
        status_code=422,
        content={"detail": "; ".join(messages)},
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
