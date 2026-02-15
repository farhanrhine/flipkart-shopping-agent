# ==============================================================================
# DOCKERFILE - Flipkart Shopping Agent
# ==============================================================================
# This Dockerfile builds a container for the Flask application.
#
# BUILD COMMAND:
#   docker build -t flipkart-shopping-agent .
#
# RUN COMMAND:
#   docker run -p 5000:5000 --env-file .env flipkart-shopping-agent
#
# FOR KUBERNETES:
#   docker build -t your-dockerhub-username/flipkart-shopping-agent:latest .
#   docker push your-dockerhub-username/flipkart-shopping-agent:latest
# ==============================================================================

# Use Python 3.12 slim image (matches pyproject.toml)
FROM python:3.12-slim

# Set working directory inside container
# - Creates isolated /app folder inside the container (not on your local machine)
# - All subsequent commands (COPY, RUN, CMD) execute within this directory
# - Keeps application files organized and prevents conflicts with system files
WORKDIR /app

# Set environment variables
# - Prevents Python from writing .pyc files
# - Ensures output is sent straight to terminal (for logging)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# - gcc and python3-dev needed for some Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer)
RUN pip install uv

# Copy dependency files first (for Docker layer caching)
COPY pyproject.toml .
COPY uv.lock* ./

# Install Python dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application code
COPY . .

# Expose port 5000 (Flask default)
EXPOSE 5000

# Health check - Kubernetes/Docker can use this
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run the Flask application
# Use gunicorn for production (more stable than Flask dev server)
CMD ["python", "app.py"]

# ==============================================================================
# FOR PRODUCTION: Use gunicorn instead of Flask dev server
# Uncomment the line below and comment the CMD above
# ==============================================================================
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
