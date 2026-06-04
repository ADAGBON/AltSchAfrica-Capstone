# Course Enrollment Platform API

A secure, database-backed RESTful API built with **FastAPI** for managing users, courses, and enrollments. It implements JWT authentication, role-based access control (RBAC), PostgreSQL with Alembic migrations, and a full automated test suite.

**Live API:** https://altschafrica-capstone.onrender.com/docs

## Tech Stack

- **FastAPI** — web framework
- **PostgreSQL** — relational database
- **SQLAlchemy 2.0** — ORM
- **Alembic** — database migrations
- **python-jose** + **passlib/bcrypt** — JWT auth and password hashing
- **pytest** — automated tests

## Features

- JWT-based register and login with bcrypt password hashing
- RBAC with separate `student` and `admin` permissions
- Public course reads; admin-only create, update, activate/deactivate, delete
- Student enroll/deregister; admin oversight of all enrollments
- Business rules: unique emails and course codes, capacity limits, duplicate-enrollment and inactive-course prevention
- Layered architecture: routers → services → repositories

## Project Structure

```
app/
├── core/           # Security, exceptions
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic request/response models
├── repositories/   # Database access layer
├── services/       # Business logic layer
├── routers/        # API endpoints
├── config.py
├── database.py
├── dependencies.py
└── main.py
alembic/            # Database migrations
tests/              # Automated API tests
scripts/            # Admin-seeding utility
Dockerfile          # API container image
docker-compose.yml  # PostgreSQL + API stack
```

## Prerequisites

- **Docker option:** Docker Desktop (or Docker Engine + Docker Compose v2)
- **Local option:** Python 3.11+ and PostgreSQL 14+

---

## Setup Instructions

You can run the project either with Docker (simplest) or locally with your own Python environment.

### Option A — Docker (recommended)

This builds the API, starts PostgreSQL, **runs migrations automatically**, and launches the server with a single command:

```bash
git clone https://github.com/ADAGBON/AltSchAfrica-Capstone.git
cd AltSchAfrica-Capstone
docker compose up --build
```

Once it's running, the interactive API docs are at **http://127.0.0.1:8000/docs**.

Useful Docker commands:

| Command | Description |
|---------|-------------|
| `docker compose up --build` | Build images and start services |
| `docker compose up -d` | Start in the background |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Stop and delete the database volume |
| `docker compose logs -f api` | Follow API logs |

### Option B — Local (without Docker)

**1. Clone the repository and create a virtual environment**

```bash
git clone https://github.com/ADAGBON/AltSchAfrica-Capstone.git
cd AltSchAfrica-Capstone
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment variables**

Copy the example file and edit the values:

```bash
cp .env.example .env       # macOS / Linux
# copy .env.example .env   # Windows
```

`.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/enrollment_db
SECRET_KEY=your-long-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**4. Create the database**

```sql
CREATE DATABASE enrollment_db;
```

**5. Run migrations** (see the section below), then **start the API:**

```bash
uvicorn app.main:app --reload
```

API docs: **http://127.0.0.1:8000/docs**

---

## How to Run Migrations

The project uses **Alembic** for database migrations.

- **With Docker:** migrations run automatically every time the container starts — you don't need to do anything.
- **Locally:** apply all migrations to bring the database schema up to date:

```bash
alembic upgrade head
```

Other useful migration commands:

```bash
alembic current                                      # Show the current migration revision
alembic downgrade -1                                 # Roll back the last migration
alembic revision --autogenerate -m "your message"    # Generate a new migration
```

---

## How to Run Tests

The test suite uses an in-memory SQLite database, so **no PostgreSQL setup is required to run the tests**.

```bash
pytest -v
```

This runs the full suite covering every endpoint — authentication, user profile, course management, enrollment rules, and administrative oversight.

---

## Deploying to Render

The repo ships with a `Dockerfile`, so Render can build and run it directly. The container entrypoint runs `alembic upgrade head` and then starts the server, so migrations apply automatically on every deploy.

1. **Create a PostgreSQL instance** — In the Render dashboard: *New → PostgreSQL*. Once it's created, copy its **Internal Database URL**.
2. **Create the web service** — *New → Web Service*, connect this GitHub repo, and let Render auto-detect the `Dockerfile` (Runtime: **Docker**).
3. **Set environment variables** on the web service:

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | The Postgres URL from step 1 (see note below) |
   | `SECRET_KEY` | A long random string (e.g. `openssl rand -hex 32`) |

4. **Deploy.** When the build finishes, your interactive docs are live — for this project, at https://altschafrica-capstone.onrender.com/docs.

> **Note 1 — URL scheme:** Render hands out database URLs that start with `postgres://`, but SQLAlchemy 2.0 only accepts `postgresql://`. Change the scheme when you paste it in: `postgresql://user:pass@host/dbname`.

> **Note 2 — port binding:** Render sets a `PORT` environment variable it expects the app to listen on. The container exposes `8000`, which Render auto-detects for Docker services, so the default works. If you ever hit a port-binding error, change the last line of `docker-entrypoint.sh` to bind dynamically:
> ```sh
> exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
> ```

After deploying, create your admin user by opening a shell on the Render service and running `python -m scripts.seed_admin` with the `ADMIN_*` variables set (see "Creating an Admin" below).

---

## Creating an Admin

Public registration always creates a **student** (this prevents privilege escalation through the public endpoint). To create an admin, seed one directly:

```bash
ADMIN_NAME="Site Admin" \
ADMIN_EMAIL="admin@example.com" \
ADMIN_PASSWORD="a-long-strong-password" \
python -m scripts.seed_admin
```

The script is idempotent and will promote an existing user to admin if the email already exists.

## API Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register` | Public | Register a user (always a student) |
| POST | `/auth/login` | Public | Log in and receive a JWT |
| GET | `/users/me` | Authenticated | Get current user profile |
| GET | `/courses` | Public | List active courses |
| GET | `/courses/{id}` | Public | Get a course by ID |
| POST | `/courses` | Admin | Create a course |
| PUT | `/courses/{id}` | Admin | Update a course |
| PATCH | `/courses/{id}/activate` | Admin | Activate a course |
| PATCH | `/courses/{id}/deactivate` | Admin | Deactivate a course |
| DELETE | `/courses/{id}` | Admin | Delete a course |
| POST | `/enrollments` | Student | Enroll in a course |
| DELETE | `/enrollments/course/{id}` | Student | Deregister from a course |
| GET | `/enrollments` | Admin | View all enrollments |
| GET | `/enrollments/course/{id}` | Admin | View enrollments for a course |
| DELETE | `/enrollments/{id}` | Admin | Remove a student enrollment |
| GET | `/health` | Public | Health check |

## Role-Based Access Control

| Action | Student | Admin |
|--------|---------|-------|
| View courses | Yes | Yes |
| Enroll in course | Yes | No |
| Deregister from course | Yes | No |
| Create / update / delete course | No | Yes |
| View all enrollments | No | Yes |
| Remove enrollment | No | Yes |

## Example Usage

```bash
# Register and log in
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@uni.com","password":"password123"}'

curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@uni.com","password":"password123"}'

# Use the returned access_token for authenticated requests
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer <your_token>"
```

## License

Educational capstone project.
