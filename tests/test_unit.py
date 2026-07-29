from unittest.mock import Mock
import pytest
from notification_engine import NotificationEngine, WalletRepository, SMSGatewayClient


def test_validation_boundary():
    repo, primary = Mock(spec=WalletRepository), Mock(spec=SMSGatewayClient)
    repo.get_status.return_value, primary.send_sms.return_value = "PENDING", True
    engine = NotificationEngine(repo, primary)

    assert engine.dispatch("msg1", "+250780000000", "Hello") == "SENT_PRIMARY"
    repo.get_status.reset_mock()

    for phone in ["0780000000", "+00012"]:
        with pytest.raises(ValueError):
            engine.dispatch("msg2", phone, "Hello")
        repo.get_status.assert_not_called()


def test_idempotency_mock_check():
    repo, primary = Mock(spec=WalletRepository), Mock(spec=SMSGatewayClient)
    repo.get_status.return_value = "SENT"
    engine = NotificationEngine(repo, primary)

    assert engine.dispatch("msg1", "+250780000000", "Hello") == "ALREADY_SENT"
    primary.send_sms.assert_not_called()


def test_retry_logic_verification():
    repo, primary = Mock(spec=WalletRepository), Mock(spec=SMSGatewayClient)
    repo.get_status.return_value = "PENDING"
    primary.send_sms.side_effect = [Exception("Timeout"), True]

    engine = NotificationEngine(repo, primary)
    assert engine.dispatch("msg1", "+250780000000", "Hello") == "SENT_PRIMARY"
    assert primary.send_sms.call_count == 2
    repo.save_status.assert_called_with("msg1", "+250780000000", "SENT")


def test_fallback_gateway_failover():
    repo, primary, backup = Mock(spec=WalletRepository), Mock(spec=SMSGatewayClient), Mock(spec=SMSGatewayClient)
    repo.get_status.return_value = "PENDING"
    primary.send_sms.side_effect = [Exception("Fail1"), Exception("Fail2")]
    backup.send_sms.return_value = True

    engine = NotificationEngine(repo, primary, backup)
    assert engine.dispatch("msg1", "+250780000000", "Hello") == "SENT_BACKUP"
    assert primary.send_sms.call_count == 2
    repo.save_status.assert_called_with("msg1", "+250780000000", "SENT_BACKUP")


def test_complete_failure_path():
    repo, primary, backup = Mock(spec=WalletRepository), Mock(spec=SMSGatewayClient), Mock(spec=SMSGatewayClient)
    repo.get_status.return_value = "PENDING"
    primary.send_sms.side_effect = Exception("P_Fail")
    backup.send_sms.side_effect = Exception("B_Fail")

    engine = NotificationEngine(repo, primary, backup)
    with pytest.raises(RuntimeError):
        engine.dispatch("msg1", "+250780000000", "Hello")
    repo.save_status.assert_called_with("msg1", "+250780000000", "FAILED")
