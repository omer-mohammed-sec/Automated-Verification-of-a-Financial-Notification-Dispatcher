# Financial Notification Dispatcher API

**Software Verification & Testing Project**  
**Registration Number:** `30027/2025`  

---

## 📌 Project Overview

This project provides an automated verification, testing, and continuous integration system for a **Financial Notification Dispatcher** core engine (`NotificationEngine`).

The system implements retry logic across primary and backup telecom gateways, idempotency checks against a wallet repository, and failure handling verified through unit tests with mocks and integration tests against an in-memory SQLite database.

---

## 📋 Requirements

Dependencies specified in `requirements.txt`:

```text
pytest
pytest-cov
```

---

## 🛠️ Installation & Execution Instructions

### 1. Create and Activate Virtual Environment
```bash
python -m venv venv

# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Linux / macOS:
source venv/bin/activate
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run Tests
```bash
pytest -v
```

### 4. Run Coverage Report
```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=90
```

---

## 📂 Project Structure

```text
financial_notification_dispatcher/
├── notification_engine.py      # Core Application Logic (starter code)
├── requirements.txt            # Dependencies (pytest, pytest-cov)
├── pytest.ini                  # Pytest configuration file
├── conftest.py                 # Pytest path import configuration
├── .gitignore                  # Git exclusion rules for Python
├── README.md                   # Project documentation and student registration
├── docs/                       # Documentation and reports directory
│   └── report.html             # Test Execution HTML Report
├── tests/                      # Test suite directory
│   ├── test_unit.py            # Unit tests using Mock objects
│   └── test_integration.py     # Integration tests with SQLite database
└── .github/
    └── workflows/
        └── ci.yml              # Continuous Integration (CI) workflow
```
