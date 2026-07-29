# Automated Verification of a Financial Notification Dispatcher

**Course:** Software Verification and Validation  
**Registration Number:** 30027  
**Year:** 2025  

---

## 📌 Project Overview

This project implements an automated verification, testing, and continuous integration (CI) suite for a **Financial Notification Dispatcher** core business engine (`NotificationEngine`). 

The architecture guarantees reliable SMS dispatching by supporting retry logic across primary and backup telecom gateways, idempotency checks against a wallet repository, and rigorous failure handling.

---

## 🧪 Phase 1: Pure Testing Strategy

### 1. Unit Test Suite (`tests/test_unit.py`)
Executed in total isolation using `unittest.mock.Mock` (0.09s total runtime, zero network/database calls):
- **Validation Boundary Test**: Verifies valid E.164 phone numbers (`+250780000000`) and asserts invalid formats (`0780000000`, `+00012`) raise `ValueError` without querying the database.
- **Idempotency Mock Check**: Confirms that if `repo.get_status()` returns `"SENT"`, `dispatch()` returns `"ALREADY_SENT"` without invoking SMS gateways.
- **Retry Logic Verification**: Verifies primary gateway retries upon failure and records status `"SENT"` upon succeeding on attempt 2.
- **Fallback Gateway Failover**: Primary gateway fails twice; backup gateway succeeds, returning `"SENT_BACKUP"`.
- **Complete Failure Path**: Primary and backup gateways fail; verifies status `"FAILED"` is saved and `RuntimeError` is raised.

### 2. Integration Test Suite (`tests/test_integration.py`)
Tested against a real in-memory SQLite database (`:memory:`):
- **Pytest Fixture**: Initializes table `messages(msg_id TEXT, phone TEXT, status TEXT)`.
- **Successful Dispatch Verification**: Confirms real SQLite table record insertion with `status='SENT'`.
- **"Mock Lie" Demonstration**: Demonstrates that unit tests using `Mock(spec=WalletRepository)` pass even when the database query uses an invalid table (`msg_logs`), whereas real integration tests correctly fail with `sqlite3.OperationalError: no such table: msg_logs`.

---

## ⚙️ Phase 2: Continuous Integration (GitHub Actions)

Configured in `.github/workflows/ci.yml`:
- **Automated Triggers**: Fires on `push` and `pull_request` to `main`.
- **Multi-Version Matrix**: Evaluates on **Python 3.10** and **Python 3.11** (`ubuntu-latest`).
- **Fail-Fast Workflow**:
  1. **Run Unit Tests**: `pytest tests/test_unit.py -v`
  2. **Run Integration Tests**: `pytest tests/test_integration.py -v`
  3. **Enforce Coverage (>=90%)**: `pytest --cov=. --cov-report=term-missing --cov-fail-under=90`

---

## 🚀 How to Run Locally

### 1. Install Dependencies
```bash
pip install pytest pytest-cov
```

### 2. Run All Tests
```bash
pytest -v
```

### 3. Run Coverage Enforcement
```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=90
```

---

## 📁 Repository Structure

```text
Software-Verification-and-validation/
├── README.md                       # Project documentation
├── STUDENT_INFO.md                 # Registration information
├── notification_engine.py          # Core Business Application Code
├── conftest.py                     # Pytest root module import path configuration
├── pytest.ini                      # Pytest runner configuration
├── .gitignore                      # Git exclusion rules
├── tests/
│   ├── test_unit.py                # Isolated Mock Unit Tests
│   └── test_integration.py         # Real SQLite Integration Tests
└── .github/
    └── workflows/
        └── ci.yml                  # GitHub Actions CI Workflow
```
