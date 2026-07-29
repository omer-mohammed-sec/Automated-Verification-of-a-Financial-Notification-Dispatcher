# Practical Exam: Automated Verification of a Financial Notification Dispatcher

Student Registration Number: 30027  
Year: 2025  
Course: Software Verification, Testing & CI/CD  

## Description

This project contains the solution for the practical exam on software verification and testing. It implements automated tests and a continuous integration pipeline for a financial notification engine (NotificationEngine).

The application logic handles sending SMS notifications through primary and backup gateways, checking message status for idempotency, and handling gateway failures.

## Project Structure

- notification_engine.py: Core application logic (provided starter code).
- tests/test_unit.py: Unit tests using unittest.mock.Mock.
- tests/test_integration.py: Integration tests using an in-memory SQLite database.
- .github/workflows/ci.yml: GitHub Actions continuous integration pipeline.
- requirements.txt: Project dependencies (pytest and pytest-cov).
- conftest.py: Import path configuration for pytest.
- pytest.ini: Pytest settings.
- .gitignore: Git exclusion rules for Python.
- README.md: Project documentation.

## Phase 1: Testing Strategy

### Unit Tests (tests/test_unit.py)
The unit tests run completely in memory with zero database or network calls.

1. test_validation_boundary: Tests valid phone numbers (+250780000000) and ensures invalid numbers (0780000000, +00012) raise a ValueError without querying the repository.
2. test_idempotency_mock_check: Verifies that if get_status() returns 'SENT', dispatch() returns 'ALREADY_SENT' and does not call send_sms().
3. test_retry_logic_verification: Checks that if the primary gateway fails on the first attempt and succeeds on the second attempt, send_sms() is called twice and status is saved as 'SENT'.
4. test_fallback_gateway_failover: Tests that when the primary gateway fails twice, the backup gateway is used and status 'SENT_BACKUP' is returned.
5. test_complete_failure_path: Verifies that when both gateways fail, status 'FAILED' is saved and a RuntimeError is raised.

### Integration Tests (tests/test_integration.py)
The integration tests run against a real in-memory SQLite database (:memory:).

1. db_connection fixture: Initializes an in-memory SQLite database with a messages table (msg_id TEXT, phone TEXT, status TEXT).
2. test_successful_dispatch_integration: Dispatches a message and verifies that the record status is saved as 'SENT' in SQLite.
3. test_mock_lie_demonstration: Demonstrates the 'Mock Lie' by showing that unit tests pass with mocked repository calls even if an incorrect table name is used, while integration tests fail with a SQLite error.

## Phase 2: Continuous Integration

The GitHub Actions workflow (.github/workflows/ci.yml) automates testing on push or pull request to the main branch.

- OS: ubuntu-latest
- Python Versions: 3.10 and 3.11
- Pipeline Steps:
  1. Installs pytest and pytest-cov.
  2. Runs Unit Tests (pytest tests/test_unit.py -v).
  3. Runs Integration Tests (pytest tests/test_integration.py -v).
  4. Enforces minimum 90% coverage (pytest --cov=. --cov-report=term-missing --cov-fail-under=90).

## How to Run

Install dependencies:
pip install -r requirements.txt

Run test suite:
pytest -v

Run test coverage:
pytest --cov=. --cov-report=term-missing --cov-fail-under=90
