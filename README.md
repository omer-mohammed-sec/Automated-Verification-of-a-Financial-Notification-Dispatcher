# Automated Verification of a Financial Notification Dispatcher

**Student Registration Number:** 30027/2025  
**Course:** Software Verification and validation


## Project Overview

This repository contains the complete implementation and verification suite for the **Financial Notification Engine** (`NotificationEngine`), developed for the Practical Examination in *Software Verification, Testing & CI/CD*.

The service dispatches financial SMS notifications through primary and backup telecom gateways while enforcing:
- **E.164 Phone Format Validation** (`+` prefix followed by 2 to 15 digits)
- **Idempotency** (returning `ALREADY_SENT` if message status is `SENT`)
- **Primary Gateway Retries** (up to 2 attempts upon transient errors)
- **Backup Gateway Failover** (fallback delivery returning `SENT_BACKUP`)
- **Terminal Failure Logging** (persisting `FAILED` status and raising `RuntimeError`)

## Project Structure

```text
financial_notification_dispatcher/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD Pipeline
├── tests/
│   ├── test_unit.py           # Phase 1: In-Memory Unit Tests (Mocking)
│   └── test_integration.py    # Phase 1: Real SQLite Integration Tests
├── notification_engine.py     # Core Application Logic
├── requirements.txt           # Project Dependencies (pytest, pytest-cov)
├── README.md                  # Project Documentation
└── .gitignore                 # Git Exclusion Rules
```

## Testing Strategy

### 1. Unit Tests (`tests/test_unit.py`)
Executes 100% in memory using `unittest.mock.Mock` with zero database calls:
- `test_validation_boundary`: Validates `+250780000000` and raises `ValueError` for `0780000000` and `+00012` without querying the repository.
- `test_idempotency_mock_check`: Confirms status `SENT` immediately returns `ALREADY_SENT` without sending SMS.
- `test_retry_logic_verification`: Confirms 1st attempt failure retries primary gateway and saves `SENT`.
- `test_fallback_gateway_failover`: Confirms 2 primary failures fail over to backup gateway, returning `SENT_BACKUP`.
- `test_complete_failure_path`: Confirms failure of all gateways saves `FAILED` and raises `RuntimeError`.

### 2. Integration Tests (`tests/test_integration.py`)
Runs against a real in-memory SQLite database (`:memory:`):
- `db_connection` fixture: Initializes table `messages(msg_id TEXT, phone TEXT, status TEXT)`.
- `test_successful_dispatch_integration`: Dispatches via primary gateway and verifies `status = 'SENT'` in SQLite.
- `test_mock_lie_demonstration`: Demonstrates that unit tests with mocks pass despite incorrect table names (`msg_logs`), whereas real integration tests fail with `sqlite3.OperationalError`.

## Continuous Integration Pipeline (`.github/workflows/ci.yml`)

Automated verification on GitHub Actions:
- **Matrix:** Python `3.10` & `3.11` on `ubuntu-latest`.
- **Order:** Unit tests first (fail-fast), Integration tests second.
- **Coverage:** Enforces minimum **90% coverage** (`--cov-fail-under=90`).

## Running Tests Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests with coverage check
pytest -v --cov=. --cov-report=term-missing --cov-fail-under=90
```

## Test Execution Summary

- **Test Results:** 7 / 7 PASSED (100%)
- **Execution Time:** ~0.36 seconds
- **Code Coverage:** **100.00%**
