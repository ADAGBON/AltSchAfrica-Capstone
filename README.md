# Course Enrollment Platform API

A secure, database-backed RESTful API built with **FastAPI** for managing users, courses, and enrollments. The system implements JWT authentication, role-based access control (RBAC), and comprehensive automated tests.

**Live API:** `https://<your-service-name>.onrender.com/docs` _(replace with your deployed URL)_

## Features

- **Authentication**: JWT-based register and login with bcrypt password hashing
- **RBAC**: Separate permissions for `student` and `admin` roles
- **Course management**: Public read access; admin-only create, update, activate/deactivate, delete
- **Enrollment management**: Students enroll/deregister; admins oversee all enrollments
- **Business rules**: Unique emails/course codes, capacity limits, duplicate enrollment prevention
- **PostgreSQL** with Alembic migrations
- **Layered architecture**: routers → services → repositories

## Project Structure

```
app/
├── core/           # Security, exceptions, HTTP helpers
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
Dockerfile          # API container image
docker-compose.yml  # PostgreSQL + API stack
```

## Prerequisites

**Local development**

- Python 3.11+
- PostgreSQL 14+

**Docker deployment**

- Docker Desktop (or Docker Engine + Docker Compose v2)

## Docker Deployment (recommended)

Run the full stack (PostgreSQL + API + automatic migrations) with one command:

```bash
docker compose up --build
```

The API will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Docker commands

| Command | Description |
|---------|-------------|
| `docker compose up --build` | Build images and start services |
| `docker compose up -d` | Start in the background |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Stop and delete database volume |
| `docker compose logs -f api` | Follow API logs |

### Production notes

Before deploying to a cloud host, set a strong secret in your environment:

```bash
# Windows PowerShell
$env:SECRET_KEY="your-long-random-production-secret"
docker compose up --build -d
```

Or create a `.env` file in the project root (Docker Compose reads `SECRET_KEY` from it):

```env
SECRET_KEY=your-long-random-production-secret
```

The `api` service connects to PostgreSQL using hostname `db` inside the Docker network. Migrations run automatically on container start.

## Deploying to Render

The repo ships with a `Dockerfile`, so Render can build and run it directly. The container entrypoint runs `alembic upgrade head` and then starts the server, so migrations apply automatically on every deploy.

1. **Create a PostgreSQL instance** — In the Render dashboard: *New → PostgreSQL*. Once it's created, copy its **Internal Database URL**.
2. **Create the web service** — *New → Web Service*, connect this GitHub repo, and let Render auto-detect the `Dockerfile` (Runtime: **Docker**).
3. **Set environment variables** on the web service:

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | The Postgres URL from step 1 (see note below) |
   | `SECRET_KEY` | A long random string (e.g. `openssl rand -hex 32`) |

4. **Deploy.** When the build finishes, your interactive docs are live at `https://<your-service-name>.onrender.com/docs`.

> **Note 1 — URL scheme:** Render hands out database URLs that start with `postgres://`, but SQLAlchemy 2.0 only accepts `postgresql://`. Change the scheme when you paste it in: `postgresql://user:pass@host/dbname`.

> **Note 2 — port binding:** Render sets a `PORT` environment variable it expects the app to listen on. The container exposes `8000`, which Render auto-detects for Docker services, so the default works. If you ever hit a port-binding error, change the last line of `docker-entrypoint.sh` to bind dynamically:
> ```sh
> exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
> ```

After deploying, create your admin user by opening a shell on the Render service and running `python -m scripts.seed_admin` with the `ADMIN_*` variables set (see "Creating an admin" below).

## Local Setup (without Docker)

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/ADAGBON/AltSchAfrica-Capstone.git
cd AltSchAfrica-Capstone
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy the example env file and update values:

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/enrollment_db
SECRET_KEY=your-long-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Create the database

```sql
CREATE DATABASE enrollment_db;
```

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Running Tests

Tests use an in-memory SQLite database (no PostgreSQL required for tests):

```bash
pytest -v
```

## API Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register` | Public | Register a user |
| POST | `/auth/login` | Public | Login and receive JWT |
| GET | `/users/me` | Authenticated | Get current user profile |
| GET | `/courses` | Public | List active courses |
| GET | `/courses/{id}` | Public | Get course by ID |
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
| Create/update/delete course | No | Yes |
| View all enrollments | No | Yes |
| Remove enrollment | No | Yes |

## Example Usage

### Register and login

Public registration always creates a **student**. (Admins are provisioned
separately — see "Creating an admin" below.)

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@uni.com","password":"password123"}'

curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@uni.com","password":"password123"}'
```

Use the returned `access_token` in subsequent requests:

```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer <your_token>"
```

### Creating an admin

The public endpoint cannot create admins (that would be a privilege-escalation
hole). Seed one out-of-band instead:

```bash
ADMIN_NAME="Site Admin" \
ADMIN_EMAIL="admin@example.com" \
ADMIN_PASSWORD="a-long-strong-password" \
python -m scripts.seed_admin
```

The script is idempotent and will promote an existing user to admin if the
email already exists.

## Assessment Alignment

This project addresses all core requirements:

- JWT authentication with hashed passwords
- PostgreSQL relational database with migrations
- RBAC for students and admins
- Enrollment business rules (capacity, duplicates, inactive courses)
- Request validation and meaningful error responses
- Automated tests for every endpoint
- Service/repository layered architecture

## License

Educational capstone project.
