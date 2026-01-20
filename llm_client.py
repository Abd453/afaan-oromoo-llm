"""
LLM Client module with enhanced error handling and retry logic
"""

import os
import time
import logging
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Custom Exceptions ====================

class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class RateLimitError(LLMError):
    """Rate limit exceeded error."""
    pass


class APIKeyError(LLMError):
    """API key is invalid or missing."""
    pass


class NetworkError(LLMError):
    """Network connectivity error."""
    pass


class ModelNotFoundError(LLMError):
    """Requested model not available."""
    pass


class ContentFilterError(LLMError):
    """Content was filtered by safety settings."""
    pass


# ==================== Configuration ====================

# Configure Gemini API
if not Config.GEMINI_API_KEY:
    logger.error("⚠️ GEMINI_API_KEY not found in environment")
else:
    genai.configure(api_key=Config.GEMINI_API_KEY)


# ==================== Helper Functions ====================

def parse_error(error_msg: str) -> tuple:
    """
    Parse error message and return appropriate exception type and user message.
    
    Returns:
        Tuple of (ExceptionClass, user_friendly_message)
    """
    error_lower = error_msg.lower()
    
    if "404" in error_msg or "not found" in error_lower:
        return (
            ModelNotFoundError,
            f"Rakkoo: Model '{Config.MODEL_NAME}' hin argamne. "
            "Furmaata: 'pip install --upgrade google-generativeai' fidhaa."
        )
    
    elif "429" in error_msg or "rate limit" in error_lower or "quota" in error_lower:
        return (
            RateLimitError,
            "Rakkoo: Gaaffii baay'ee erguuf yaaltan. Maaloo turuuf eeggatanii irra deebi'aa."
        )
    
    elif "401" in error_msg or "403" in error_msg or "api key" in error_lower:
        return (
            APIKeyError,
            "Rakkoo: API Key sirrii miti. Maaloo qindeessaa keessan sakatta'aa."
        )
    
    elif "400" in error_msg or "invalid" in error_lower:
        return (
            LLMError,
            "Rakkoo: Gaaffiin keessan sirrii miti. Maaloo gara biraa yaalaa."
        )
    
    elif "blocked" in error_lower or "safety" in error_lower:
        return (
            ContentFilterError,
            "Rakkoo: Qabiyyeen kun nageenyaan cufameera. Maaloo gaaffii biraa yaslaa."
        )
    
    elif "network" in error_lower or "connection" in error_lower or "timeout" in error_lower:
        return (
            NetworkError,
            "Rakkoo: Walitti dhufeenya interneetii. Maaloo interneetii keessan sakatta'aa."
        )
    
    else:
        return (
            LLMError,
            f"Rakkoo teeknikaa (VPN?): {error_msg}"
        )


def exponential_backoff(attempt: int, base_delay: float = 1.0) -> float:
    """Calculate exponential backoff delay."""
    return min(base_delay * (2 ** attempt), 30)  # Max 30 seconds


def manage_context(history: List[Dict], max_messages: int = None) -> List[Dict]:
    """
    Manage conversation context to stay within limits.
    
    Args:
        history: List of message dictionaries
        max_messages: Maximum number of messages to keep (default from config)
        
    Returns:
        Truncated history
    """
    if max_messages is None:
        max_messages = Config.MAX_HISTORY_LENGTH
    
    if len(history) <= max_messages:
        return history
    
    # Keep most recent messages
    return history[-max_messages:]


# ==================== Main Query Function ====================

def query_llm(
    user_input: str,
    history_input: List[Dict] = None,
    task_type: str = "default",
    max_retries: int = None
) -> str:
    """
    Query the LLM with enhanced error handling and retry logic.
    
    Args:
        user_input: User's input text
        history_input: Conversation history
        task_type: Type of task for config selection (default, creative, factual, translation, code)
        max_retries: Maximum number of retry attempts (default from config)
        
    Returns:
        Model's response text
        
    Raises:
        Various LLMError subclasses on failure
    """
    if history_input is None:
        history_input = []
    
    if max_retries is None:
        max_retries = Config.MAX_RETRIES
    
    # Validate input
    if not user_input or not user_input.strip():
        return "Maaloo, gaaffii keessan barreessaa."
    
    if len(user_input) > Config.MAX_INPUT_LENGTH:
        return f"Rakkoo: Gaaffiin dheeraa dha (max {Config.MAX_INPUT_LENGTH} arfii)."
    
    # Manage context window
    history_input = manage_context(history_input)
    
    # Get appropriate configuration
    generation_config = Config.get_generation_config(task_type)
    
    # Retry loop
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"Querying LLM (attempt {attempt + 1}/{max_retries + 1})")
            
            # Create model instance
            model = genai.GenerativeModel(
                model_name=Config.MODEL_NAME,
                generation_config=generation_config,
                system_instruction=Config.SYSTEM_INSTRUCTION
            )
            
            # Format history for Gemini
            gemini_history = []
            for msg in history_input:
                role = "user" if msg.get('role') == "user" else "model"
                parts = msg.get('parts', [])
                if not isinstance(parts, list):
                    parts = [parts]
                gemini_history.append({"role": role, "parts": parts})
            
            # Start chat and get response
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(user_input)
            
            logger.info("Query successful")
            return response.text
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM Error (attempt {attempt + 1}): {error_msg}")
            
            # Parse error
            exception_class, user_message = parse_error(error_msg)
            last_error = exception_class(user_message)
            
            # Don't retry for certain errors
            if exception_class in [APIKeyError, ModelNotFoundError, ContentFilterError]:
                logger.error(f"Non-retryable error: {exception_class.__name__}")
                return user_message
            
            # Check if we should retry
            if attempt < max_retries:
                # For rate limits, use exponential backoff
                if exception_class == RateLimitError:
                    delay = exponential_backoff(attempt, Config.RETRY_DELAY)
                    logger.info(f"Rate limited. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                # For network errors, shorter delay
                elif exception_class == NetworkError:
                    delay = Config.RETRY_DELAY
                    logger.info(f"Network error. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                # For other errors, minimal delay
                else:
                    time.sleep(0.5)
            else:
                logger.error(f"Max retries ({max_retries}) exceeded")
                return user_message
    
    # If we get here, all retries failed
    if last_error:
        return str(last_error)
    
    return "Rakkoo: Deebii argachuu hin dandeenye. Maaloo irra deebi'ii yaalaa."


# ==================== Fallback and Caching (Optional) ====================

# Simple in-memory cache for common queries
_response_cache = {}

def query_llm_with_cache(user_input: str, history_input: List[Dict] = None, **kwargs) -> str:
    """
    Query LLM with simple caching for common questions.
    Note: Only caches queries without history.
    """
    cache_key = user_input.strip().lower()
    
    # Only cache if no history
    if not history_input and cache_key in _response_cache:
        logger.info("Cache hit")
        return _response_cache[cache_key]
    
    response = query_llm(user_input, history_input, **kwargs)
    
    # Cache successful responses without history
    if not history_input and len(_response_cache) < 100:  # Limit cache size
        _response_cache[cache_key] = response
    
    return response


# ==================== Testing Helper ====================

def test_connection() -> bool:
    """
    Test LLM connection and configuration.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        response = query_llm("Test", max_retries=1)
        return "Rakkoo" not in response
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection
    print("Testing LLM connection...")
    if test_connection():
        print("✓ Connection successful!")
    else:
        print("✗ Connection failed. Check your configuration.")
