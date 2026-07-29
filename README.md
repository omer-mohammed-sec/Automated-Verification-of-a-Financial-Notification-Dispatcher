# Practical Exam: Automated Verification of a Financial Notification Dispatcher

**Student Registration Number:** 30027  
**Year:** 2025  
**Course:** Software Verification, Testing & CI/CD  

---

## Overview

This repository contains the solution for the practical examination on automated software verification. The project focuses on verifying the core business logic of a financial notification dispatcher (`NotificationEngine`).

The project consists of two main phases:
- **Phase 1**: Unit testing with mocks (`unittest.mock.Mock`) and integration testing with a real in-memory SQLite database.
- **Phase 2**: Automated Continuous Integration (CI) pipeline using GitHub Actions.

---

## Project Structure

```text
.
├── notification_engine.py      # Core application logic (provided starter code)
├── tests/
│   ├── test_unit.py            # Unit tests using Mock objects
│   └── test_integration.py     # Integration tests with SQLite database
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI workflow
├── STUDENT_INFO.md             # Student registration details
└── README.md                   # Project documentation
```

---

## Phase 1: Pure Testing Strategy

### 1. Unit Tests (`tests/test_unit.py`)
Executes entirely in memory without contacting any external service or database.
- `test_validation_boundary`: Checks valid phone numbers (`+250780000000`) and asserts invalid formats (`0780000000`, `+00012`) raise `ValueError` without querying the database repository.
- `test_idempotency_mock_check`: Verifies that if `get_status()` returns `'SENT'`, the dispatcher returns `'ALREADY_SENT'` and skips sending SMS.
- `test_retry_logic_verification`: Confirms primary gateway retries upon failure and records status `'SENT'` when attempt 2 succeeds.
- `test_fallback_gateway_failover`: Verifies that when the primary gateway fails twice, the backup gateway is invoked and status `'SENT_BACKUP'` is returned.
- `test_complete_failure_path`: Tests total failure where both gateways fail, asserting status `'FAILED'` is saved and `RuntimeError` is raised.

### 2. Integration Tests (`tests/test_integration.py`)
Tests against a real in-memory SQLite database (`:memory:`).
- `db_connection` fixture: Initializes an in-memory SQLite database table `messages(msg_id TEXT, phone TEXT, status TEXT)`.
- `test_successful_dispatch_integration`: Dispatches a message and verifies that the row with `status='SENT'` is inserted into the SQLite database.
- `test_mock_lie_demonstration`: Demonstrates the "Mock Lie" scenario where unit tests using `Mock(spec=WalletRepository)` pass despite targeting an invalid table name (`msg_logs`), whereas real integration tests fail with `sqlite3.OperationalError`.

---

## Phase 2: Continuous Integration (GitHub Actions)

The workflow file `.github/workflows/ci.yml` automates the testing process on GitHub:
- **Triggers**: On push or pull request to the `main` branch.
- **Matrix**: Runs on Python 3.10 and Python 3.11 (`ubuntu-latest`).
- **Steps**:
  1. Installs dependencies (`pytest`, `pytest-cov`).
  2. Runs Unit Tests (`pytest tests/test_unit.py -v`).
  3. Runs Integration Tests (`pytest tests/test_integration.py -v`).
  4. Checks test coverage (`pytest --cov=. --cov-report=term-missing --cov-fail-under=90`).

---

## How to Run

### Install Dependencies
```bash
pip install pytest pytest-cov
```

### Run Tests
```bash
pytest -v
```

### Check Coverage
```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=90
```
