"""
Integration tests for API endpoints
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, Mock
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient


@pytest.fixture
def test_app():
    """Create test FastAPI app with temporary database."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
        db_path = f.name
    
    # Set environment variable for test database
    os.environ['DATABASE_PATH'] = db_path
    os.environ['ALLOWED_ORIGINS'] = '*'
    
    # Import app after setting environment
    from app import app
    
    client = TestClient(app)
    yield client
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


class TestChatEndpoint:
    """Test /chat endpoint."""
    
    @patch('app.query_llm')
    def test_chat_basic(self, mock_query, test_app):
        """Test basic chat request."""
        mock_query.return_value = "Nagaan jira!"
        
        response = test_app.post(
            "/chat",
            json={"user_input": "Akkam jirta?", "history": []}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['response'] == "Nagaan jira!"
        assert 'response_time' in data
    
    @patch('app.query_llm')
    def test_chat_with_history(self, mock_query, test_app):
        """Test chat with conversation history."""
        mock_query.return_value = "Deebii"
        
        history = [
            {"role": "user", "parts": ["Hello"]},
            {"role": "model", "parts": ["Hi"]}
        ]
        
        response = test_app.post(
            "/chat",
            json={
                "user_input": "Continue",
                "history": history
            }
        )
        
        assert response.status_code == 200
        assert mock_query.called
        # Check history was passed
        call_args = mock_query.call_args
        assert call_args[0][1] == history
    
    @patch('app.query_llm')
    def test_chat_with_session_id(self, mock_query, test_app):
        """Test chat with session_id saves to database."""
        mock_query.return_value = "Response"
        
        # Create session first
        test_app.post("/sessions", json={
            "session_id": "test-session",
            "title": "Test"
        })
        
        # Send chat with session_id
        response = test_app.post(
            "/chat",
            json={
                "user_input": "Hello",
                "session_id": "test-session"
            }
        )
        
        assert response.status_code == 200
        
        # Verify messages were saved
        session_response = test_app.get("/sessions/test-session")
        session_data = session_response.json()
        assert len(session_data['messages']) == 2  # User + model
    
    def test_chat_empty_input(self, test_app):
        """Test chat with empty input."""
        response = test_app.post(
            "/chat",
            json={"user_input": "", "history": []}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_too_long_input(self, test_app):
        """Test chat with input exceeding max length."""
        long_input = "a" * 3000
        
        response = test_app.post(
            "/chat",
            json={"user_input": long_input, "history": []}
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.query_llm')
    def test_chat_llm_error(self, mock_query, test_app):
        """Test chat when LLM raises an error."""
        mock_query.side_effect = Exception("LLM Error")
        
        response = test_app.post(
            "/chat",
            json={"user_input": "Test", "history": []}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data['status'] == 'error'


class TestSessionEndpoints:
    """Test session management endpoints."""
    
    def test_create_session(self, test_app):
        """Test creating a new session."""
        response = test_app.post(
            "/sessions",
            json={
                "session_id": "new-session",
                "title": "New Session"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['session']['id'] == "new-session"
        assert data['session']['title'] == "New Session"
    
    def test_list_sessions(self, test_app):
        """Test listing sessions."""
        # Create a few sessions
        for i in range(3):
            test_app.post("/sessions", json={
                "session_id": f"session-{i}",
                "title": f"Session {i}"
            })
        
        response = test_app.get("/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert len(data['sessions']) == 3
        assert 'total' in data
    
    def test_list_sessions_with_pagination(self, test_app):
        """Test listing sessions with limit and offset."""
        # Create sessions
        for i in range(5):
            test_app.post("/sessions", json={
                "session_id": f"sess-{i}",
                "title": f"Session {i}"
            })
        
        response = test_app.get("/sessions?limit=2&offset=1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['sessions']) == 2
    
    def test_get_session(self, test_app):
        """Test getting a specific session."""
        # Create session
        test_app.post("/sessions", json={
            "session_id": "get-session",
            "title": "Get Test"
        })
        
        response = test_app.get("/sessions/get-session")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['session']['id'] == "get-session"
        assert 'messages' in data
    
    def test_get_nonexistent_session(self, test_app):
        """Test getting a session that doesn't exist."""
        response = test_app.get("/sessions/nonexistent")
        
        assert response.status_code == 404
    
    def test_update_session(self, test_app):
        """Test updating a session."""
        # Create session
        test_app.post("/sessions", json={
            "session_id": "update-session",
            "title": "Original"
        })
        
        # Update it
        response = test_app.put(
            "/sessions/update-session",
            json={"title": "Updated"}
        )
        
        assert response.status_code == 200
        
        # Verify update
        get_response = test_app.get("/sessions/update-session")
        data = get_response.json()
        assert data['session']['title'] == "Updated"
    
    def test_delete_session(self, test_app):
        """Test deleting a session."""
        # Create session
        test_app.post("/sessions", json={
            "session_id": "delete-session",
            "title": "To Delete"
        })
        
        # Delete it
        response = test_app.delete("/sessions/delete-session")
        
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
        
        # Verify it's gone
        get_response = test_app.get("/sessions/delete-session")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_session(self, test_app):
        """Test deleting a session that doesn't exist."""
        response = test_app.delete("/sessions/nonexistent")
        
        assert response.status_code == 404


class TestAnalyticsEndpoint:
    """Test analytics endpoint."""
    
    @patch('app.query_llm')
    def test_get_analytics(self, mock_query, test_app):
        """Test getting analytics data."""
        mock_query.return_value = "Response"
        
        # Generate some activity
        test_app.post("/sessions", json={"session_id": "s1", "title": "Session 1"})
        test_app.post("/chat", json={"user_input": "Test", "session_id": "s1"})
        
        response = test_app.get("/analytics")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'summary' in data
        assert 'total_sessions' in data
        assert 'total_messages' in data
        assert data['total_sessions'] >= 1
    
    @patch('app.query_llm')
    def test_analytics_with_date_filter(self, mock_query, test_app):
        """Test analytics with date filtering."""
        mock_query.return_value = "Response"
        
        response = test_app.get(
            "/analytics?start_date=2026-01-01&end_date=2026-12-31"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'


class TestHomeEndpoint:
    """Test home page endpoint."""
    
    def test_home_page(self, test_app):
        """Test that home page loads."""
        response = test_app.get("/")
        
        # Should return HTML
        assert response.status_code in [200, 404]  # 404 if index.html not found in test
        if response.status_code == 200:
            assert 'text/html' in response.headers.get('content-type', '')


class TestCORSHeaders:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self, test_app):
        """Test that CORS headers are set."""
        response = test_app.options("/chat")
        
        # Should have CORS headers
        assert 'access-control-allow-origin' in response.headers


class TestRateLimiting:
    """Test rate limiting (note: may need to adjust based on config)."""
    
    @patch('app.query_llm')
    def test_rate_limit_not_exceeded_normal_use(self, mock_query, test_app):
        """Test that normal use doesn't trigger rate limit."""
        mock_query.return_value = "Response"
        
        # Make a few requests (well below limit)
        for _ in range(3):
            response = test_app.post(
                "/chat",
                json={"user_input": "Test", "history": []}
            )
            assert response.status_code == 200


class TestInputValidation:
    """Test input validation."""
    
    def test_missing_user_input(self, test_app):
        """Test request with missing user_input field."""
        response = test_app.post(
            "/chat",
            json={"history": []}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_json(self, test_app):
        """Test request with invalid JSON."""
        response = test_app.post(
            "/chat",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

