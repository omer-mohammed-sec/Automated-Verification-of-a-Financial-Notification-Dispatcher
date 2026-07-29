from unittest.mock import Mock
import pytest
from notification_engine import NotificationEngine, WalletRepository, SMSGatewayClient


def test_validation_boundary():
    mock_repo = Mock(spec=WalletRepository)
    mock_primary = Mock(spec=SMSGatewayClient)
    mock_repo.get_status.return_value = "PENDING"
    mock_primary.send_sms.return_value = True

    engine = NotificationEngine(mock_repo, mock_primary)
    assert engine.dispatch("msg1", "+250780000000", "Hello") == "SENT_PRIMARY"

    mock_repo.get_status.reset_mock()
    for phone in ["0780000000", "+00012"]:
        with pytest.raises(ValueError):
            engine.dispatch("msg2", phone, "Hello")
        mock_repo.get_status.assert_not_called()


def test_idempotency_mock_check():
    mock_repo = Mock(spec=WalletRepository)
    mock_primary = Mock(spec=SMSGatewayClient)
    mock_repo.get_status.return_value = "SENT"

    engine = NotificationEngine(mock_repo, mock_primary)
    assert engine.dispatch("msg1", "+250780000000", "Hello") == "ALREADY_SENT"
    mock_primary.send_sms.assert_not_called()


def test_retry_logic_verification():
    mock_repo = Mock(spec=WalletRepository)
    mock_primary = Mock(spec=SMSGatewayClient)
    mock_repo.get_status.return_value = "PENDING"
    mock_primary.send_sms.side_effect = [Exception("Error"), True]

    engine = NotificationEngine(mock_repo, mock_primary)
    assert engine.dispatch("msg1", "+250780000000", "Hello") == "SENT_PRIMARY"
    assert mock_primary.send_sms.call_count == 2
    mock_repo.save_status.assert_called_with("msg1", "+250780000000", "SENT")


def test_fallback_gateway_failover():
    mock_repo = Mock(spec=WalletRepository)
    mock_primary = Mock(spec=SMSGatewayClient)
    mock_backup = Mock(spec=SMSGatewayClient)

    mock_repo.get_status.return_value = "PENDING"
    mock_primary.send_sms.side_effect = [Exception("Fail 1"), Exception("Fail 2")]
    mock_backup.send_sms.return_value = True

    engine = NotificationEngine(mock_repo, mock_primary, mock_backup)
    assert engine.dispatch("msg1", "+250780000000", "Hello") == "SENT_BACKUP"
    assert mock_primary.send_sms.call_count == 2
    mock_repo.save_status.assert_called_with("msg1", "+250780000000", "SENT_BACKUP")


def test_complete_failure_path():
    mock_repo = Mock(spec=WalletRepository)
    mock_primary = Mock(spec=SMSGatewayClient)
    mock_backup = Mock(spec=SMSGatewayClient)

    mock_repo.get_status.return_value = "PENDING"
    mock_primary.send_sms.side_effect = Exception("Primary Error")
    mock_backup.send_sms.side_effect = Exception("Backup Error")

    engine = NotificationEngine(mock_repo, mock_primary, mock_backup)

    with pytest.raises(RuntimeError):
        engine.dispatch("msg1", "+250780000000", "Hello")

    mock_repo.save_status.assert_called_with("msg1", "+250780000000", "FAILED")
