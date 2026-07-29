import sqlite3
from unittest.mock import Mock
import pytest
from notification_engine import NotificationEngine, WalletRepository, SMSGatewayClient


class SQLiteWalletRepository(WalletRepository):
    """Real SQLite repository implementation for integration testing."""

    def __init__(self, db_conn, table_name="messages"):
        self.conn = db_conn
        self.table_name = table_name

    def get_status(self, msg_id: str) -> str:
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT status FROM {self.table_name} WHERE msg_id = ?", (msg_id,)
        )
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
    """Fixture that initializes an in-memory SQLite database with the messages table."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE messages (
            msg_id TEXT,
            phone TEXT,
            status TEXT
        )
        """
    )
    conn.commit()
    yield conn
    conn.close()


def test_successful_dispatch_integration(db_connection):
    """Execute a successful dispatch and verify SQLite contains status='SENT'."""
    repo = SQLiteWalletRepository(db_connection, table_name="messages")
    mock_primary = Mock(spec=SMSGatewayClient)
    mock_primary.send_sms.return_value = True

    engine = NotificationEngine(repo, mock_primary)
    status_result = engine.dispatch("msg_001", "+250780000000", "Integration Test Message")

    assert status_result == "SENT_PRIMARY"

    # Query SQLite directly to verify insertion
    cursor = db_connection.cursor()
    cursor.execute("SELECT status FROM messages WHERE msg_id = ?", ("msg_001",))
    row = cursor.fetchone()

    assert row is not None
    assert row[0] == "SENT"


def test_mock_lie_demonstration(db_connection):
    """
    Demonstrates the 'Mock Lie':
    - In Unit Tests: Using Mock(spec=WalletRepository) passes because save_status() is mocked out.
    - In Integration Tests: Using a repository configured with 'msg_logs' fails with sqlite3.OperationalError
      because table 'msg_logs' does not exist in the real database (table is 'messages').
    """
    # 1. UNIT TEST BEHAVIOR WITH MOCK (Unit Test PASSES despite bad table name in real logic)
    mock_repo = Mock(spec=WalletRepository)
    mock_repo.get_status.return_value = None
    mock_primary = Mock(spec=SMSGatewayClient)
    mock_primary.send_sms.return_value = True

    mock_engine = NotificationEngine(mock_repo, mock_primary)
    # Unit test succeeds because save_status SQL is never executed against SQLite
    unit_result = mock_engine.dispatch("msg_002", "+250780000000", "Hello")
    assert unit_result == "SENT_PRIMARY"

    # 2. INTEGRATION TEST BEHAVIOR WITH REAL DB (Integration Test FAILS due to SQL error)
    faulty_repo = SQLiteWalletRepository(db_connection, table_name="msg_logs")
    real_engine = NotificationEngine(faulty_repo, mock_primary)

    # Real database execution fails because table 'msg_logs' does not exist in SQLite schema
    with pytest.raises(sqlite3.OperationalError, match="no such table: msg_logs"):
        real_engine.dispatch("msg_002", "+250780000000", "Hello")
