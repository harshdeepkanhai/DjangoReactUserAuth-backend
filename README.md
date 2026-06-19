# DjangoReactUserAuth — Backend

A production-grade Django **6.0** REST API providing JWT user authentication
(register, login, token refresh, logout, current user) for the companion
[React frontend](https://github.com/harshdeepkanhai/DjangoReactUserAuth-frontend).

Built with Django REST Framework + [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/),
a custom user model, 12-factor environment configuration, and container/CI tooling.

> **Upgraded from Django 2.2.** The old `djangorestframework-jwt` library (now
> unmaintained) was replaced by `djangorestframework-simplejwt`, so the auth
> contract changed — see [API](#api) below. The frontend must be updated to use
> the `access` token and the refresh flow.

---

## Tech stack

| Concern        | Choice                                                   |
| -------------- | -------------------------------------------------------- |
| Framework      | Django 6.0.6, Django REST Framework 3.17                 |
| Auth           | SimpleJWT (access + refresh, rotation + blacklist)       |
| User model     | Custom `accounts.User` (username login, unique email)    |
| Config         | `django-environ` (12-factor), split settings             |
| DB             | SQLite (dev) / PostgreSQL (prod) via `DATABASE_URL`      |
| API docs       | drf-spectacular (OpenAPI 3 + Swagger UI)                 |
| Static files   | WhiteNoise                                               |
| Server         | Gunicorn                                                 |
| Tests / lint   | pytest-django, factory-boy, ruff                         |
| CI / container | GitHub Actions, Docker + docker-compose                  |

## Project layout

```
config/            project package (settings split, urls, wsgi, asgi)
  settings/        base.py · local.py · production.py
accounts/          auth app: custom User, serializers, views, throttles, tests
requirements/      base.txt · local.txt · production.txt
Dockerfile · docker-compose.yml · .github/workflows/ci.yml
```

## Local development

Requires **Python 3.12+** (tested on 3.14).

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |    Unix: source .venv/bin/activate
pip install -r requirements/local.txt

cp .env.example .env          # then set DJANGO_SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is served at `http://localhost:8000/`. Interactive docs:
`http://localhost:8000/api/docs/`.

### Environment variables

All configuration comes from the environment (see [.env.example](.env.example)).
Key variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`,
`DATABASE_URL`, `CORS_ALLOWED_ORIGINS`. Generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

## API

Base path: `/api/v1/auth/`. All bodies are JSON. Protected endpoints require
`Authorization: Bearer <access>`.

| Method | Path                          | Auth    | Body                                       | Response                          |
| ------ | ----------------------------- | ------- | ------------------------------------------ | --------------------------------- |
| POST   | `/api/v1/auth/register/`      | none    | `username, email, password[, first_name, last_name]` | `201 {user, access, refresh}` |
| POST   | `/api/v1/auth/login/`         | none    | `username, password`                       | `200 {access, refresh, user}`     |
| POST   | `/api/v1/auth/login/refresh/` | none    | `refresh`                                  | `200 {access}`                    |
| POST   | `/api/v1/auth/logout/`        | bearer  | `refresh`                                  | `205` (refresh blacklisted)       |
| GET    | `/api/v1/auth/me/`            | bearer  | —                                          | `200 {id, username, email, ...}`  |

Utility endpoints: `GET /health/` (liveness + DB check), `GET /api/schema/`
(OpenAPI), `GET /api/docs/` (Swagger UI), `/admin/` (Django admin).

Access tokens live 15 minutes; refresh tokens 7 days and rotate on use (the old
refresh token is blacklisted after rotation).

### Example

```bash
# Register (returns tokens — the client is immediately logged in)
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"jane","email":"jane@example.com","password":"Sup3rStr0ng!pw"}'

# Use the access token
curl http://localhost:8000/api/v1/auth/me/ -H "Authorization: Bearer <access>"
```

## Tests & linting

```bash
pytest                 # full suite (pytest-django)
ruff check .           # lint
ruff format .          # format
```

## Docker

```bash
cp .env.example .env   # set DJANGO_SECRET_KEY; keep DATABASE_URL pointing at db
docker compose up --build
```

This starts Gunicorn (`web`) behind PostgreSQL 17 (`db`), runs migrations on
boot, and serves on `http://localhost:8000/`. The `web` service uses
`config.settings.production`.

## Production notes

- Set `DJANGO_SETTINGS_MODULE=config.settings.production`.
- Provide `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`,
  and a PostgreSQL `DATABASE_URL` — production settings have **no insecure
  defaults**.
- Validate the security posture with `python manage.py check --deploy`.
- Production enables HSTS, secure cookies, SSL redirect, and serves hashed,
  compressed static assets via WhiteNoise.
