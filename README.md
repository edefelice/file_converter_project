# File Converter DevSecOps

A secure file converter application demonstrating DevSecOps best practices.

## Branches

- **main** (this branch): Secure version with all vulnerabilities fixed
- **insecure**: Educational branch with intentional vulnerabilities

## Security Fixes Applied

| Vulnerability | OWASP | Fix |
|--------------|-------|-----|
| Command Injection | A03 | subprocess.run() with argument lists |
| Path Traversal | A01 | secure_filename() + path validation |
| Insecure Deserialization | A08 | JSON instead of pickle |
| Security Misconfiguration | A05 | DEBUG=False, random SECRET_KEY |
| Insecure Design | A04 | File size limits, proper validation |
| Vulnerable Dependencies | A06 | Updated all packages |

## Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app/app.py
```

## Running with Docker
```bash
docker build -t file-converter .
docker run -p 5001:5000 file-converter
```

## DevSecOps Pipeline

The Jenkins pipeline includes:
- **Bandit**: Python SAST
- **Trivy**: Container scanning
- **OWASP ZAP**: DAST

## Author:

Ernesto De Felice
Project for System Security exam - DevSecOps demonstration