# Base image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Set entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Expose port
EXPOSE 8000


# Run Django server
CMD ["gunicorn", "shelly_project.wsgi:application", "--bind", "0.0.0.0:8000"]
