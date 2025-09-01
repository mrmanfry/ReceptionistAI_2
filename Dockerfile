# Receptionist AI - Multi-tenant AI Receptionist Service
# Build timestamp: 2025-09-01 19:00:00
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY config.py .
COPY database/ ./database/

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
