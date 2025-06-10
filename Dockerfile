FROM python:3.11-slim

# Create non-root user
RUN useradd -m appuser
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appuser /app
USER appuser

ENV DICOMWEB_URL="" \
    DICOMWEB_USER="" \
    DICOMWEB_PASS=""

HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

