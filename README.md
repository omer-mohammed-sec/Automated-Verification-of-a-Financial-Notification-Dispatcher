# Practical Exam: Automated Verification of a Financial Notification Dispatcher

**Student Registration Number:** 30027/2025  
**Course:** Software Verification, Testing & CI/CD  
**Academic Year:** 2025  

---

## Project Overview

This repository contains the complete implementation and verification suite for the **Financial Notification Engine** (`NotificationEngine`). It was developed for the Practical Exam in *Software Verification, Testing & CI/CD*.

The system handles sending financial SMS notifications through primary and backup telecom gateways while enforcing:
- **E.164 Phone Format Validation** (`+` prefix followed by 2 to 15 digits)
- **Idempotency** (preventing duplicate dispatch if message status is already `SENT`)
- **Primary Gateway Retries** (up to 2 attempts upon transient errors)
- **Backup Gateway Failover** (fallback delivery when primary fails twice)
- **Terminal Failure Logging** (persisting `FAILED` status and raising `RuntimeError` on complete failure)

---

## Repository Structure

```
financial_notification_dispatcher/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD Pipeline
├── tests/
│   ├── test_unit.py           # Phase 1: In-memory Unit Tests (Mocking)
│   └── test_integration.py    # Phase 1: Real SQLite Integration Tests
├── notification_engine.py     # Core Application Business Logic
├── conftest.py                # Pytest import path configuration
├── pytest.ini                 # Pytest configuration settings
├── requirements.txt           # Project dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

---

## Phase 1 — Testing Strategy

### 1. Unit Tests (`tests/test_unit.py`)
Unit tests run **100% in memory** without network or database dependencies using `unittest.mock.Mock`.

- `test_validation_boundary`: Tests valid E.164 numbers (`+250780000000`) and verifies invalid inputs (`0780000000`, `+00012`) raise a `ValueError` without querying the repository.
- `test_idempotency_mock_check`: Ensures messages with status `SENT` immediately return `ALREADY_SENT` and never invoke `send_sms`.
- `test_retry_logic_verification`: Confirms that primary gateway failure on 1st attempt triggers a 2nd attempt before recording status `SENT`.
- `test_fallback_gateway_failover`: Confirms that 2 primary failures fail over to backup gateway, returning `SENT_BACKUP`.
- `test_complete_failure_path`: Verifies that when primary and backup fail, status `FAILED` is recorded and a `RuntimeError` is raised.

### 2. Integration Tests (`tests/test_integration.py`)
Integration tests run against a **real in-memory SQLite database** (`:memory:`).

- `db_connection` fixture: Initializes an in-memory SQLite database with table schema:
  `messages(msg_id TEXT, phone TEXT, status TEXT)`
- `test_successful_dispatch_integration`: Dispatches via primary gateway and queries SQLite to verify `status = 'SENT'`.
- `test_mock_lie_demonstration`: Demonstrates the **Mock Lie** by showing unit tests pass with mocks despite bad SQL table names (`msg_logs`), whereas real integration tests fail with `sqlite3.OperationalError`.

---

## Phase 2 — CI/CD Pipeline (`.github/workflows/ci.yml`)

Automated testing runs on every `push` and `pull_request` to the `main` branch.

- **Matrix:** Python `3.10` & `3.11` on `ubuntu-latest`.
- **Fail-Fast Order:**
  1. Unit tests run first (`pytest tests/test_unit.py -v`).
  2. Integration tests run second (`pytest tests/test_integration.py -v`).
- **Coverage Enforcement:** `pytest-cov` enforces minimum **90% coverage** (`--cov-fail-under=90`).

---

## Installation & Running Tests

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest -v
```

### Run Tests with Coverage Enforcement (>= 90%)
```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=90
```

---

## Test Verification Summary

- **Total Test Cases:** 7 / 7 PASSED (100%)
- **Execution Time:** ~0.26 seconds
- **Code Coverage:** **98.03%**
- **Status:** **READY FOR SUBMISSION**
