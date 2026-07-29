import sqlite3
from unittest.mock import Mock
import pytest
from notification_engine import NotificationEngine, WalletRepository, SMSGatewayClient


class SQLiteWalletRepository(WalletRepository):
    def __init__(self, conn, table_name="messages"):
        self.conn = conn
        self.table_name = table_name

    def get_status(self, msg_id: str) -> str:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT status FROM {self.table_name} WHERE msg_id = ?", (msg_id,))
        row = cursor.fetchone()
        return row[0] if row else None

    def save_status(self, msg_id: str, phone: str, status: str):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO {self.table_name} (msg_id, phone, status) VALUES (?, ?, ?)",
            (msg_id, phone, status),
        )
        self.conn.commit()


@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE messages (msg_id TEXT, phone TEXT, status TEXT)")
    conn.commit()
    yield conn
    conn.close()


def test_successful_dispatch_integration(db_connection):
    repo = SQLiteWalletRepository(db_connection, table_name="messages")
    mock_primary = Mock(spec=SMSGatewayClient)
    mock_primary.send_sms.return_value = True

    engine = NotificationEngine(repo, mock_primary)
    assert engine.dispatch("msg1", "+250780000000", "Hello") == "SENT_PRIMARY"

    cursor = db_connection.cursor()
    cursor.execute("SELECT status FROM messages WHERE msg_id = ?", ("msg1",))
    row = cursor.fetchone()
    assert row and row[0] == "SENT"


def test_mock_lie_demonstration(db_connection):
    mock_repo = Mock(spec=WalletRepository)
    mock_repo.get_status.return_value = None
    mock_primary = Mock(spec=SMSGatewayClient)
    mock_primary.send_sms.return_value = True

    mock_engine = NotificationEngine(mock_repo, mock_primary)
    assert mock_engine.dispatch("msg1", "+250780000000", "Hello") == "SENT_PRIMARY"

    faulty_repo = SQLiteWalletRepository(db_connection, table_name="msg_logs")
    real_engine = NotificationEngine(faulty_repo, mock_primary)

    with pytest.raises(sqlite3.OperationalError):
        real_engine.dispatch("msg1", "+250780000000", "Hello")
