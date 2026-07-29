import sys, os, sqlite3; sys.path.insert(0, os.path.abspath("."))
from unittest.mock import Mock
import pytest
from notification_engine import NotificationEngine, WalletRepository, SMSGatewayClient


class SQLiteWalletRepository(WalletRepository):
    def __init__(self, conn, table_name="messages"):
        self.conn = conn
        self.table_name = table_name

    def get_status(self, msg_id: str) -> str:
        row = self.conn.cursor().execute(f"SELECT status FROM {self.table_name} WHERE msg_id = ?", (msg_id,)).fetchone()
        return row[0] if row else None

    def save_status(self, msg_id: str, phone: str, status: str):
        self.conn.cursor().execute(f"INSERT INTO {self.table_name} VALUES (?, ?, ?)", (msg_id, phone, status))
        self.conn.commit()


@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    conn.cursor().execute("CREATE TABLE messages (msg_id TEXT, phone TEXT, status TEXT)")
    conn.commit()
    yield conn
    conn.close()


def test_successful_dispatch_integration(db_connection):
    repo, primary = SQLiteWalletRepository(db_connection, "messages"), Mock(spec=SMSGatewayClient, **{"send_sms.return_value": True})
    assert NotificationEngine(repo, primary).dispatch("m1", "+250780000000", "hi") == "SENT_PRIMARY"
    row = db_connection.cursor().execute("SELECT status FROM messages WHERE msg_id = 'm1'").fetchone()
    assert row and row[0] == "SENT"


def test_mock_lie_demonstration(db_connection):
    mock_repo, primary = Mock(spec=WalletRepository, **{"get_status.return_value": None}), Mock(spec=SMSGatewayClient, **{"send_sms.return_value": True})
    assert NotificationEngine(mock_repo, primary).dispatch("m1", "+250780000000", "hi") == "SENT_PRIMARY"
    with pytest.raises(sqlite3.OperationalError):
        NotificationEngine(SQLiteWalletRepository(db_connection, "msg_logs"), primary).dispatch("m1", "+250780000000", "hi")
