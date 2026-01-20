"""
Configuration module for Afaan Oromo LLM System
Centralizes all configuration with environment-based settings
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()


class Config:
    """Application configuration with validation."""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))
    TOP_P: float = float(os.getenv("TOP_P", "0.95"))
    TOP_K: int = int(os.getenv("TOP_K", "40"))
    
    # System Instructions
    SYSTEM_INSTRUCTION: str = os.getenv(
        "SYSTEM_INSTRUCTION",
        """You are a helpful AI assistant specialized in Afaan Oromoo language and culture.

Key Guidelines:
- Respond primarily in Afaan Oromoo unless the user explicitly requests another language
- Be culturally aware of Oromo traditions, history, and social contexts
- Handle mixed language inputs (Afaan Oromoo-English code-switching) appropriately
- Use appropriate honorifics and respectful language
- When explaining technical concepts, provide both Afaan Oromoo terms and clear explanations
- If you don't know something specific to Oromo culture, be honest about it
- Be helpful, patient, and educational in your responses"""
    )
    
    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "conversations.db")
    
    # API Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: str = os.getenv("RATE_LIMIT_PER_MINUTE", "30/minute")
    
    # Input Validation
    MAX_INPUT_LENGTH: int = int(os.getenv("MAX_INPUT_LENGTH", "2000"))
    MAX_HISTORY_LENGTH: int = int(os.getenv("MAX_HISTORY_LENGTH", "20"))
    
    # Timeouts and Retries
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "1.0"))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate critical configuration values.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError if configuration is invalid
        """
        errors = []
        
        # Check required fields
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required")
        
        # Validate ranges
        if not (0.0 <= cls.TEMPERATURE <= 2.0):
            errors.append("TEMPERATURE must be between 0.0 and 2.0")
        
        if not (0.0 <= cls.TOP_P <= 1.0):
            errors.append("TOP_P must be between 0.0 and 1.0")
        
        if cls.MAX_OUTPUT_TOKENS < 1:
            errors.append("MAX_OUTPUT_TOKENS must be positive")
        
        if cls.MAX_INPUT_LENGTH < 1:
            errors.append("MAX_INPUT_LENGTH must be positive")
        
        if cls.MAX_RETRIES < 0:
            errors.append("MAX_RETRIES must be non-negative")
        
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True
    
    @classmethod
    def get_generation_config(cls, task_type: str = "default") -> Dict[str, Any]:
        """
        Get generation configuration for specific task types.
        
        Args:
            task_type: Type of task (default, creative, factual, translation)
            
        Returns:
            Dictionary with generation configuration
        """
        configs = {
            "default": {
                "temperature": cls.TEMPERATURE,
                "max_output_tokens": cls.MAX_OUTPUT_TOKENS,
                "top_p": cls.TOP_P,
                "top_k": cls.TOP_K,
            },
            "creative": {
                "temperature": 0.9,
                "max_output_tokens": cls.MAX_OUTPUT_TOKENS,
                "top_p": 0.95,
                "top_k": 40,
            },
            "factual": {
                "temperature": 0.3,
                "max_output_tokens": 1024,
                "top_p": 0.9,
                "top_k": 20,
            },
            "translation": {
                "temperature": 0.5,
                "max_output_tokens": 1536,
                "top_p": 0.95,
                "top_k": 30,
            },
            "code": {
                "temperature": 0.4,
                "max_output_tokens": cls.MAX_OUTPUT_TOKENS,
                "top_p": 0.9,
                "top_k": 30,
            }
        }
        
        return configs.get(task_type, configs["default"])
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)."""
        print("\n" + "="*60)
        print("Afaan Oromo LLM Configuration")
        print("="*60)
        print(f"Environment:        {cls.ENVIRONMENT}")
        print(f"Debug:              {cls.DEBUG}")
        print(f"Model:              {cls.MODEL_NAME}")
        print(f"Max Output Tokens:  {cls.MAX_OUTPUT_TOKENS}")
        print(f"Temperature:        {cls.TEMPERATURE}")
        print(f"Database:           {cls.DATABASE_PATH}")
        print(f"Host:Port:          {cls.HOST}:{cls.PORT}")
        print(f"Rate Limit:         {cls.RATE_LIMIT_PER_MINUTE}")
        print(f"Max Retries:        {cls.MAX_RETRIES}")
        print(f"API Key:            {'✓ Set' if cls.GEMINI_API_KEY else '✗ Missing'}")
        print("="*60 + "\n")


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"\n⚠️  Configuration Error:\n{e}\n")
    if Config.ENVIRONMENT == "production":
        raise


# Export for convenience
def get_config() -> Config:
    """Get configuration instance."""
    return Config

