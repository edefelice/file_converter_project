# File Converter


## 📋 Description

Educational project demonstrating the implementation of a complete DevSecOps pipeline for detecting and fixing vulnerabilities in a Flask web application.

The application provides file conversion functionality and integrates automated security checks into the CI/CD pipeline.

## ⚠️ Branch Strategy

### 🔴 Branch `insecure` (Educational)
Contains intentional vulnerabilities from **OWASP Top 10:2021** for educational purposes:
- **A01**: Broken Access Control (Path Traversal)
- **A03**: Injection (Command Injection)
- **A04**: Insecure Design (lack of validation, rate limiting)
- **A05**: Security Misconfiguration (debug mode, insecure container)
- **A06**: Vulnerable and Outdated Components (obsolete libraries)
- **A08**: Software and Data Integrity Failures (insecure deserialization)

**⚠️ WARNING:** This branch contains intentional vulnerabilities and should NOT be used in production.

## 🟢 Branch `main` (Production-Ready)
Secure version of the application with all vulnerabilities fixed and best practices implemented.

### 🛠️ Security Tools

The CI/CD pipeline integrates the following tools:

| Tool | Type | Purpose |
|------|------|---------|
| **Bandit** | SAST | Static analysis of Python code |
| **Trivy** | Container Security | Docker image scanning |
| **OWASP ZAP** | DAST | Dynamic testing on running application |

### 🚀 Quick Start

#### Prerequisites
- Docker
- Jenkins with Docker-in-Docker
- Python 3.9+

#### Local Installation

```bash
# Clone repository
git clone https://github.com/edefelice/file_converter_project.git
cd file_converter_project

# Checkout desired branch
git checkout insecure  # For vulnerable version
# or
git checkout main      # For secure version

# Build Docker image
docker build -t file-converter .

# Run application
docker run -d -p 5001:5000 file-converter

# Access application
# http://localhost:5001
```

### 📊 CI/CD Pipeline

```
GitHub Push → Jenkins
           ↓
    [Checkout Code]
           ↓
    [SAST - Bandit]
           ↓
    [Build Docker Image]
           ↓
    [Container Scan - Trivy]
           ↓
    [Deploy App]
           ↓
    [DAST - OWASP ZAP]
           ↓
    [Generate Reports]
```

### 📁 Project Structure

```
file_converter_project/
├── app/                    # Flask application
│   ├── __init__.py        # Package initialization
│   ├── app.py             # Main application
│   ├── converter.py       # File conversion logic
│   ├── file_handler.py    # Upload/download handling
│   ├── templates/         # HTML templates
│   │   └── index.html
│   └── static/            # Static files (CSS, JS)
├── tests/                 # Test suite
├── docs/                  # documentation
├── reports/               # Security scan reports
├── Dockerfile            # Docker configuration
├── Jenkinsfile          # CI/CD pipeline definition
├── requirements.txt     # Python dependencies
├── .gitignore          # Git exclusion rules
└── README.md           # This file
```

### 🎯 Learning Objectives

This project demonstrates:
- ✅ Deep understanding of OWASP Top 10 vulnerabilities
- ✅ Implementation of a complete DevSecOps pipeline
- ✅ Docker containerization best practices
- ✅ Git workflow with multi-branch strategy
- ✅ Systematic vulnerability remediation

### 📈 Expected Results

#### Branch `insecure`:
- Bandit detects multiple vulnerabilities (severity: HIGH)
- Trivy finds container configuration issues
- OWASP ZAP discovers runtime vulnerabilities

#### Branch `main`:
- Clean scans or minimal vulnerabilities
- Best practices implemented
- Application ready for deployment

### 🎓 Academic Context

Project developed for the **System Security** exam.

### 👤 Author

**Ernesto De Felice**

© 2026 Ernesto De Felice. All rights reserved.

### 📄 License

Educational project - Not for production use.