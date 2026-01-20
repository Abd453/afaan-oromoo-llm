"""
Unit tests for database module
"""

import pytest
import sys
from pathlib import Path
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
        db_path = f.name
    
    db = Database(db_path)
    yield db
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


class TestSessionManagement:
    """Test session CRUD operations."""
    
    def test_create_session(self, temp_db):
        """Test session creation."""
        session = temp_db.create_session("test-123", "Test Session")
        
        assert session['id'] == "test-123"
        assert session['title'] == "Test Session"
        assert session['message_count'] == 0
        assert 'created_at' in session
        assert 'last_updated' in session
    
    def test_get_session(self, temp_db):
        """Test retrieving a session."""
        temp_db.create_session("test-456", "Another Session")
        
        session = temp_db.get_session("test-456")
        
        assert session is not None
        assert session['id'] == "test-456"
        assert session['title'] == "Another Session"
    
    def test_get_nonexistent_session(self, temp_db):
        """Test retrieving a session that doesn't exist."""
        session = temp_db.get_session("nonexistent")
        assert session is None
    
    def test_list_sessions(self, temp_db):
        """Test listing sessions."""
        temp_db.create_session("sess-1", "Session 1")
        temp_db.create_session("sess-2", "Session 2")
        temp_db.create_session("sess-3", "Session 3")
        
        sessions = temp_db.list_sessions(limit=10)
        
        assert len(sessions) == 3
        # Most recent should be first
        assert sessions[0]['id'] == "sess-3"
    
    def test_list_sessions_with_limit(self, temp_db):
        """Test listing sessions with limit."""
        for i in range(5):
            temp_db.create_session(f"sess-{i}", f"Session {i}")
        
        sessions = temp_db.list_sessions(limit=2)
        
        assert len(sessions) == 2
    
    def test_update_session(self, temp_db):
        """Test updating session title."""
        temp_db.create_session("sess-update", "Original Title")
        
        temp_db.update_session("sess-update", title="Updated Title")
        
        session = temp_db.get_session("sess-update")
        assert session['title'] == "Updated Title"
    
    def test_delete_session(self, temp_db):
        """Test deleting a session."""
        temp_db.create_session("sess-delete", "To Delete")
        
        deleted = temp_db.delete_session("sess-delete")
        
        assert deleted is True
        assert temp_db.get_session("sess-delete") is None
    
    def test_delete_nonexistent_session(self, temp_db):
        """Test deleting a session that doesn't exist."""
        deleted = temp_db.delete_session("nonexistent")
        assert deleted is False


class TestMessageManagement:
    """Test message CRUD operations."""
    
    def test_add_message(self, temp_db):
        """Test adding a message to a session."""
        temp_db.create_session("sess-msg", "Message Test")
        
        msg_id = temp_db.add_message(
            session_id="sess-msg",
            role="user",
            content="Hello",
            token_count=1
        )
        
        assert isinstance(msg_id, int)
        assert msg_id > 0
    
    def test_get_messages(self, temp_db):
        """Test retrieving messages for a session."""
        temp_db.create_session("sess-msg-get", "Get Messages")
        
        temp_db.add_message("sess-msg-get", "user", "Hello")
        temp_db.add_message("sess-msg-get", "model", "Hi there")
        
        messages = temp_db.get_messages("sess-msg-get")
        
        assert len(messages) == 2
        assert messages[0]['role'] == "user"
        assert messages[0]['content'] == "Hello"
        assert messages[1]['role'] == "model"
        assert messages[1]['content'] == "Hi there"
    
    def test_message_count_update(self, temp_db):
        """Test that session message count updates."""
        temp_db.create_session("sess-count", "Count Test")
        
        temp_db.add_message("sess-count", "user", "Message 1")
        temp_db.add_message("sess-count", "model", "Message 2")
        
        session = temp_db.get_session("sess-count")
        assert session['message_count'] == 2
    
    def test_get_conversation_history(self, temp_db):
        """Test getting formatted conversation history."""
        temp_db.create_session("sess-history", "History Test")
        
        temp_db.add_message("sess-history", "user", "Question 1")
        temp_db.add_message("sess-history", "model", "Answer 1")
        
        history = temp_db.get_conversation_history("sess-history")
        
        assert len(history) == 2
        assert history[0]['role'] == "user"
        assert history[0]['parts'] == ["Question 1"]
        assert history[1]['role'] == "model"
        assert history[1]['parts'] == ["Answer 1"]
    
    def test_get_messages_with_limit(self, temp_db):
        """Test retrieving limited number of messages."""
        temp_db.create_session("sess-limit", "Limit Test")
        
        for i in range(10):
            temp_db.add_message("sess-limit", "user", f"Message {i}")
        
        messages = temp_db.get_messages("sess-limit", limit=3)
        
        # With limit, should get most recent 3
        assert len(messages) == 3
    
    def test_delete_session_cascades_messages(self, temp_db):
        """Test that deleting a session deletes its messages."""
        temp_db.create_session("sess-cascade", "Cascade Test")
        temp_db.add_message("sess-cascade", "user", "Message")
        
        temp_db.delete_session("sess-cascade")
        
        messages = temp_db.get_messages("sess-cascade")
        assert len(messages) == 0


class TestAnalytics:
    """Test analytics tracking."""
    
    def test_log_analytics(self, temp_db):
        """Test logging analytics data."""
        temp_db.create_session("sess-analytics", "Analytics Test")
        
        temp_db.log_analytics(
            session_id="sess-analytics",
            query_type="greeting",
            response_time=1.5,
            input_length=10,
            output_length=50
        )
        
        # No assertion, just checking it doesn't raise
        summary = temp_db.get_analytics_summary()
        assert summary['total_queries'] == 1
    
    def test_log_error(self, temp_db):
        """Test logging an error."""
        temp_db.log_analytics(
            error="Test error message",
            input_length=20,
            output_length=0
        )
        
        errors = temp_db.get_error_logs(limit=10)
        assert len(errors) == 1
        assert errors[0]['error'] == "Test error message"
    
    def test_analytics_summary(self, temp_db):
        """Test getting analytics summary."""
        # Log some analytics
        for i in range(5):
            temp_db.log_analytics(
                response_time=float(i),
                input_length=100,
                output_length=200
            )
        
        summary = temp_db.get_analytics_summary()
        
        assert summary['total_queries'] == 5
        assert summary['avg_response_time'] is not None
        assert summary['avg_input_length'] == 100
        assert summary['avg_output_length'] == 200
    
    def test_analytics_with_errors(self, temp_db):
        """Test analytics counting errors."""
        temp_db.log_analytics(response_time=1.0, input_length=10, output_length=50)
        temp_db.log_analytics(error="Error 1", input_length=10, output_length=0)
        temp_db.log_analytics(error="Error 2", input_length=10, output_length=0)
        
        summary = temp_db.get_analytics_summary()
        
        assert summary['total_queries'] == 3
        assert summary['error_count'] == 2


class TestUtilities:
    """Test utility methods."""
    
    def test_get_total_sessions(self, temp_db):
        """Test counting total sessions."""
        assert temp_db.get_total_sessions() == 0
        
        temp_db.create_session("s1", "Session 1")
        temp_db.create_session("s2", "Session 2")
        
        assert temp_db.get_total_sessions() == 2
    
    def test_get_total_messages(self, temp_db):
        """Test counting total messages."""
        assert temp_db.get_total_messages() == 0
        
        temp_db.create_session("s1", "Session 1")
        temp_db.add_message("s1", "user", "Hello")
        temp_db.add_message("s1", "model", "Hi")
        
        assert temp_db.get_total_messages() == 2


class TestDatabaseInitialization:
    """Test database initialization and schema."""
    
    def test_database_creates_tables(self):
        """Test that database creates tables on initialization."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
            db_path = f.name
        
        # Remove file so database has to create it
        os.unlink(db_path)
        
        db = Database(db_path)
        
        # Should be able to create session without error
        session = db.create_session("test", "Test")
        assert session is not None
        
        # Cleanup
        os.unlink(db_path)
    
    def test_database_path_default(self):
        """Test database with default path."""
        db = Database()
        assert db.db_path == "conversations.db"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

