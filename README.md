# Automated Verification of a Financial Notification Dispatcher

**Registration Number:** 30027/2025  
**Course:** Software Verification, Testing & CI/CD  

## Description
Solution for the practical exam verifying the `NotificationEngine` service. It includes unit tests with mocks, integration tests with in-memory SQLite, and a GitHub Actions CI pipeline.

## Project Structure
- `notification_engine.py`: Core business logic.
- `tests/test_unit.py`: Phase 1 unit tests (mocking, retry, failover).
- `tests/test_integration.py`: Phase 1 integration tests (SQLite, Mock Lie).
- `.github/workflows/ci.yml`: Phase 2 CI pipeline (Python 3.10/3.11, coverage >= 90%).

## Running Tests
```bash
pip install -r requirements.txt
pytest -v --cov=. --cov-fail-under=90
```
