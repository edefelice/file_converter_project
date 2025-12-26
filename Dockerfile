# File Converter Application - Dockerfile
# Branch: main (secure)


# FIX VULNERABILITY A05: Using outdated base image
# Using specific updated base image
FROM python:3.12-slim

# FIX VULNERABILITY A05: Running as root user (no USER directive)
# Creating non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Set working directory
WORKDIR /app

# FIX VULNERABILITY A05: Copying entire context (may include sensitive files)
# Copy only requirements first (better layer caching)
COPY requirements.txt .

# FIX VULNERABILITY A06: Installing updated packeges from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create upload directories with proper permissions
RUN mkdir -p uploads converted && \
    chown -R appuser:appgroup /app

# FIX A05: Switch to non-root user
USER appuser

# FIX VULNERABILITY A05: Exposing internal port without documentation
# Document exposed port
EXPOSE 5000

# FIX VULNERABILITY A05: No health check defined
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# FIX VULNERABILITY A05: Using python directly instead of production server
# Using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app.app:app"]