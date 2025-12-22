# File Converter Application - Dockerfile
# Branch: insecure
# Contains intentional security misconfiguration for educational purposes

# VULNERABILITY A05: Using outdated base image
FROM python:3.9.7

# VULNERABILITY A05: Running as root user (no USER directive)
# Container runs with full root privileges

# Set working directory
WORKDIR /app

# VULNERABILITY A05: Copying entire context (may include sensitive files)
# Should use .dockerignore to exclude unnecessary files
COPY . /app

# VULNERABILITY A06: Installing outdated packeges from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# VULNERABILITY A05: Exposing internal port without documentation
EXPOSE 5000

# VULNERABILITY A05: No health check defined
# No HEALTHCHECK instruction

# VULNERABILITY A05: Using python directly instead of production server
# Should use gunicorn or uWSGI in production
CMD ["python", "app/app.py"]