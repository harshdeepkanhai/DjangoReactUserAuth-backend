# syntax=docker/dockerfile:1

# --- Build stage: install dependencies into an isolated virtualenv --------
FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/ requirements/
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements/production.txt


# --- Runtime stage: minimal image running as a non-root user --------------
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# psycopg[binary] bundles its own libpq, so no system Postgres libs are needed.
COPY --from=builder /opt/venv /opt/venv
COPY . .

# Collect static assets (collectstatic needs no DB; supply build-only env vars).
RUN DJANGO_SECRET_KEY=build-only \
    DJANGO_ALLOWED_HOSTS=localhost \
    CORS_ALLOWED_ORIGINS=http://localhost \
    python manage.py collectstatic --noinput

RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
