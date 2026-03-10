# Use a lightweight official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables for better Python execution in containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establish the working directory in the container
WORKDIR /app

# Install system dependencies if required (Standard enterprise practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Optimize Docker layer caching by installing requirements first
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY backend/ .

# Expose dynamic ports for service communication
EXPOSE 8081 8082 8083

# Run the adapter layer to bridge HTTP calls to Lambda logic
CMD ["python", "adapter.py"]