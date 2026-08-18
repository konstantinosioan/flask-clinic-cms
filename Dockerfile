# Debian's current stable release
FROM python:3.14-slim-trixie

# Unbuffered stdout so logs actually reach `docker logs`, especially on crash; skip .pyc files and pip's version-check noise
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Non-root user; /app is owned by appuser (not just the copied files) since the app writes clinic.db and static/uploads there
RUN useradd --create-home appuser
WORKDIR /app
RUN chown appuser:appuser /app

# Install dependencies before copying the rest of the code so editing app code doesn't bust this layer's cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 8000

# Overridable at `docker run` without rebuilding, instead of baking the worker count into the image
ENV WEB_CONCURRENCY=3

# gunicorn instead of the Flask dev server; --access-logfile - is needed because gunicorn logs no requests by default
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "app:app"]
