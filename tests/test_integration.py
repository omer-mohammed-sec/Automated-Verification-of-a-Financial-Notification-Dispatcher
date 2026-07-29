import sqlite3
from unittest.mock import Mock
import pytest
from notification_engine import NotificationEngine, WalletRepository, SMSGatewayClient


class SQLiteWalletRepository(WalletRepository):
    def __init__(self, conn, table_name="messages"):
        self.conn = conn
        self.table_name = table_name

    def get_status(self, msg_id: str) -> str:
        cur = self.conn.cursor()
        cur.execute(f"SELECT status FROM {self.table_name} WHERE msg_id = ?", (msg_id,))
        row = cur.fetchone()
        return row[0] if row else None

    def save_status(self, msg_id: str, phone: str, status: str):
        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO {self.table_name} (msg_id, phone, status) VALUES (?, ?, ?)", (msg_id, phone, status))
        self.conn.commit()


@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    conn.cursor().execute("CREATE TABLE messages (msg_id TEXT, phone TEXT, status TEXT)")
    conn.commit()
    yield conn
    conn.close()


def test_successful_dispatch_integration(db_connection):
    repo = SQLiteWalletRepository(db_connection, "messages")
    primary = Mock(spec=SMSGatewayClient)
    primary.send_sms.return_value = True

    engine = NotificationEngine(repo, primary)
    assert engine.dispatch("msg1", "+250780000000", "Hello") == "SENT_PRIMARY"

    row = db_connection.cursor().execute("SELECT status FROM messages WHERE msg_id = 'msg1'").fetchone()
    assert row and row[0] == "SENT"


def test_mock_lie_demonstration(db_connection):
    mock_repo = Mock(spec=WalletRepository)
    mock_repo.get_status.return_value = None
    primary = Mock(spec=SMSGatewayClient)
    primary.send_sms.return_value = True

    assert NotificationEngine(mock_repo, primary).dispatch("msg1", "+250780000000", "Hello") == "SENT_PRIMARY"

    faulty_engine = NotificationEngine(SQLiteWalletRepository(db_connection, "msg_logs"), primary)
    with pytest.raises(sqlite3.OperationalError):
        faulty_engine.dispatch("msg1", "+250780000000", "Hello")
