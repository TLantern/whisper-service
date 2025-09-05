# Dockerfile for Whisper v3 Service
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for Whisper models
RUN mkdir -p /tmp/whisper_models

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]
