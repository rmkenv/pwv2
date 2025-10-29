FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_complete.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_complete.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
