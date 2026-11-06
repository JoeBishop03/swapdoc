FROM python:3.12-slim

# LibreOffice (headless) does the actual document conversion
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice-writer libreoffice-core fonts-dejavu fonts-liberation fonts-crosextra-carlito fonts-crosextra-caladea && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV UPLOAD_DIR=/tmp/uploads OUTPUT_DIR=/tmp/outputs PORT=8000 \
    PYTHONUNBUFFERED=1 \
    OTEL_SERVICE_NAME=swapdoc \
    OTEL_PYTHON_FLASK_EXCLUDED_URLS="healthz,static/.*,favicon.ico"
EXPOSE 8000

# two workers keep LibreOffice memory predictable; raise timeout for big files
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "180", "app:app"]
