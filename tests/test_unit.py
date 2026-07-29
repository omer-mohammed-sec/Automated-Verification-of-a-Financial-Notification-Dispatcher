import sys, os; sys.path.insert(0, os.path.abspath("."))
from unittest.mock import Mock
import pytest
from notification_engine import NotificationEngine, WalletRepository, SMSGatewayClient


def test_validation_boundary():
    repo, primary = Mock(spec=WalletRepository), Mock(spec=SMSGatewayClient)
    engine = NotificationEngine(repo, primary)
    assert engine.dispatch("m1", "+250780000000", "hi") == "SENT_PRIMARY"

    repo.get_status.reset_mock()
    for phone in ["0780000000", "+00012"]:
        with pytest.raises(ValueError):
            engine.dispatch("m2", phone, "hi")
        repo.get_status.assert_not_called()


def test_idempotency_mock_check():
    repo, primary = Mock(spec=WalletRepository, **{"get_status.return_value": "SENT"}), Mock(spec=SMSGatewayClient)
    assert NotificationEngine(repo, primary).dispatch("m1", "+250780000000", "hi") == "ALREADY_SENT"
    primary.send_sms.assert_not_called()


def test_retry_logic_verification():
    repo, primary = Mock(spec=WalletRepository), Mock(spec=SMSGatewayClient, **{"send_sms.side_effect": [Exception, True]})
    assert NotificationEngine(repo, primary).dispatch("m1", "+250780000000", "hi") == "SENT_PRIMARY"
    assert primary.send_sms.call_count == 2
    repo.save_status.assert_called_with("m1", "+250780000000", "SENT")


def test_fallback_gateway_failover():
    repo, primary, backup = Mock(spec=WalletRepository), Mock(spec=SMSGatewayClient, **{"send_sms.side_effect": [Exception, Exception]}), Mock(spec=SMSGatewayClient, **{"send_sms.return_value": True})
    assert NotificationEngine(repo, primary, backup).dispatch("m1", "+250780000000", "hi") == "SENT_BACKUP"
    assert primary.send_sms.call_count == 2
    repo.save_status.assert_called_with("m1", "+250780000000", "SENT_BACKUP")


def test_complete_failure_path():
    repo, primary, backup = Mock(spec=WalletRepository), Mock(spec=SMSGatewayClient, **{"send_sms.side_effect": Exception}), Mock(spec=SMSGatewayClient, **{"send_sms.side_effect": Exception})
    with pytest.raises(RuntimeError):
        NotificationEngine(repo, primary, backup).dispatch("m1", "+250780000000", "hi")
    repo.save_status.assert_called_with("m1", "+250780000000", "FAILED")
