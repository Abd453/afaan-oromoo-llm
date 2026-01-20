"""
Unit tests for LLM client module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_client import (
    query_llm,
    parse_error,
    exponential_backoff,
    manage_context,
    LLMError,
    RateLimitError,
    APIKeyError,
    NetworkError,
    ModelNotFoundError,
    ContentFilterError
)


class TestErrorParsing:
    """Test error message parsing and classification."""
    
    def test_parse_404_error(self):
        """Test parsing of 404 model not found error."""
        exception_class, message = parse_error("404 model not found")
        assert exception_class == ModelNotFoundError
        assert "hin argamne" in message
    
    def test_parse_rate_limit_error(self):
        """Test parsing of rate limit error."""
        exception_class, message = parse_error("429 rate limit exceeded")
        assert exception_class == RateLimitError
        assert "baay'ee" in message or "eeggatanii" in message
    
    def test_parse_api_key_error(self):
        """Test parsing of API key error."""
        exception_class, message = parse_error("401 invalid api key")
        assert exception_class == APIKeyError
        assert "API Key" in message
    
    def test_parse_network_error(self):
        """Test parsing of network error."""
        exception_class, message = parse_error("network connection timeout")
        assert exception_class == NetworkError
        assert "interneetii" in message or "walitti dhufeenya" in message.lower()
    
    def test_parse_content_filter_error(self):
        """Test parsing of content filter error."""
        exception_class, message = parse_error("content blocked by safety filters")
        assert exception_class == ContentFilterError
        assert "nageenyaan" in message


class TestExponentialBackoff:
    """Test exponential backoff calculation."""
    
    def test_first_attempt(self):
        """First attempt should have base delay."""
        delay = exponential_backoff(0, base_delay=1.0)
        assert delay == 1.0
    
    def test_second_attempt(self):
        """Second attempt should double."""
        delay = exponential_backoff(1, base_delay=1.0)
        assert delay == 2.0
    
    def test_third_attempt(self):
        """Third attempt should quadruple."""
        delay = exponential_backoff(2, base_delay=1.0)
        assert delay == 4.0
    
    def test_max_delay(self):
        """Should cap at 30 seconds."""
        delay = exponential_backoff(10, base_delay=1.0)
        assert delay == 30.0


class TestContextManagement:
    """Test conversation context management."""
    
    def test_empty_history(self):
        """Empty history should remain empty."""
        result = manage_context([])
        assert result == []
    
    def test_short_history(self):
        """Short history should remain unchanged."""
        history = [
            {"role": "user", "parts": ["hello"]},
            {"role": "model", "parts": ["hi"]}
        ]
        result = manage_context(history, max_messages=10)
        assert result == history
    
    def test_long_history_truncation(self):
        """Long history should be truncated to most recent."""
        history = [
            {"role": "user", "parts": [f"message {i}"]}
            for i in range(30)
        ]
        result = manage_context(history, max_messages=10)
        assert len(result) == 10
        assert result[0]["parts"][0] == "message 20"  # Most recent 10
        assert result[-1]["parts"][0] == "message 29"


class TestQueryLLM:
    """Test main query_llm function."""
    
    def test_empty_input(self):
        """Empty input should return error message in Oromo."""
        result = query_llm("")
        assert "gaaffii" in result.lower()
        assert "barreessaa" in result.lower()
    
    def test_whitespace_only_input(self):
        """Whitespace-only input should return error message."""
        result = query_llm("   ")
        assert "gaaffii" in result.lower()
    
    def test_too_long_input(self):
        """Input exceeding max length should return error."""
        long_input = "a" * 3000
        result = query_llm(long_input)
        assert "dheeraa" in result.lower() or "max" in result
    
    @patch('llm_client.genai.GenerativeModel')
    def test_successful_query(self, mock_model):
        """Test successful query with mocked response."""
        # Setup mock
        mock_chat = Mock()
        mock_response = Mock()
        mock_response.text = "Akkam jirta! Nagaan jira."
        mock_chat.send_message.return_value = mock_response
        
        mock_instance = Mock()
        mock_instance.start_chat.return_value = mock_chat
        mock_model.return_value = mock_instance
        
        # Execute
        result = query_llm("Akkam?")
        
        # Verify
        assert result == "Akkam jirta! Nagaan jira."
        mock_model.assert_called_once()
        mock_instance.start_chat.assert_called_once()
        mock_chat.send_message.assert_called_once_with("Akkam?")
    
    @patch('llm_client.genai.GenerativeModel')
    def test_query_with_history(self, mock_model):
        """Test query with conversation history."""
        # Setup mock
        mock_chat = Mock()
        mock_response = Mock()
        mock_response.text = "Deebii"
        mock_chat.send_message.return_value = mock_response
        
        mock_instance = Mock()
        mock_instance.start_chat.return_value = mock_chat
        mock_model.return_value = mock_instance
        
        # Execute with history
        history = [
            {"role": "user", "parts": ["Hello"]},
            {"role": "model", "parts": ["Hi"]}
        ]
        result = query_llm("Continue", history_input=history)
        
        # Verify history was passed
        call_args = mock_instance.start_chat.call_args
        assert 'history' in call_args.kwargs
        assert len(call_args.kwargs['history']) == 2
    
    @patch('llm_client.genai.GenerativeModel')
    @patch('llm_client.time.sleep')  # Mock sleep to speed up test
    def test_retry_on_rate_limit(self, mock_sleep, mock_model):
        """Test retry logic on rate limit error."""
        # Setup mock to fail twice then succeed
        mock_chat = Mock()
        mock_response = Mock()
        mock_response.text = "Success"
        
        mock_instance = Mock()
        mock_instance.start_chat.return_value = mock_chat
        
        # First two calls raise rate limit, third succeeds
        mock_chat.send_message.side_effect = [
            Exception("429 rate limit exceeded"),
            Exception("429 rate limit exceeded"),
            mock_response
        ]
        
        mock_model.return_value = mock_instance
        
        # Execute
        result = query_llm("Test", max_retries=3)
        
        # Verify retries occurred
        assert mock_chat.send_message.call_count == 3
        assert mock_sleep.call_count == 2  # Two retries mean two sleeps
        assert result == "Success"
    
    @patch('llm_client.genai.GenerativeModel')
    def test_no_retry_on_api_key_error(self, mock_model):
        """Test that API key errors don't trigger retries."""
        # Setup mock to fail with API key error
        mock_chat = Mock()
        mock_instance = Mock()
        mock_instance.start_chat.return_value = mock_chat
        mock_chat.send_message.side_effect = Exception("401 invalid api key")
        mock_model.return_value = mock_instance
        
        # Execute
        result = query_llm("Test", max_retries=3)
        
        # Verify only one attempt was made
        assert mock_chat.send_message.call_count == 1
        assert "API Key" in result


class TestHistoryFormatting:
    """Test conversation history formatting."""
    
    @patch('llm_client.genai.GenerativeModel')
    def test_history_with_string_parts(self, mock_model):
        """Test history formatting when parts is a string."""
        mock_chat = Mock()
        mock_response = Mock()
        mock_response.text = "Response"
        mock_chat.send_message.return_value = mock_response
        
        mock_instance = Mock()
        mock_instance.start_chat.return_value = mock_chat
        mock_model.return_value = mock_instance
        
        # History with string parts (not list)
        history = [
            {"role": "user", "parts": "Hello"},  # String, not list
        ]
        
        result = query_llm("Test", history_input=history)
        
        # Verify history was converted to correct format
        call_args = mock_instance.start_chat.call_args
        formatted_history = call_args.kwargs['history']
        assert isinstance(formatted_history[0]['parts'], list)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

