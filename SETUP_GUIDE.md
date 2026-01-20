# Setup Guide - Afaan Oromo LLM System

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Environment File
Create a file named `.env` in the project root with the following content:

```env
# API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Model Configuration
MODEL_NAME=gemini-2.5-flash
TEMPERATURE=0.7
MAX_OUTPUT_TOKENS=2048
TOP_P=0.95
TOP_K=40

# Database
DATABASE_PATH=conversations.db

# API Server
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Security and Rate Limiting
RATE_LIMIT_PER_MINUTE=30/minute
MAX_INPUT_LENGTH=2000
MAX_HISTORY_LENGTH=20

# Retry Configuration
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RETRY_DELAY=1.0

# Environment
ENVIRONMENT=development
DEBUG=false
```

**Important**: Replace `your_gemini_api_key_here` with your actual Google Gemini API key.

### 3. Verify Configuration
```bash
python -c "from config import Config; Config.print_config()"
```

This will validate your configuration and print current settings.

### 4. Run Tests (Optional but Recommended)
```bash
# Run all tests
pytest -v

# Run specific test categories
pytest tests/test_llm.py -v
pytest tests/test_database.py -v
pytest tests/test_api.py -v
```

### 5. Run Evaluation Suite (Optional)
```bash
# Run evaluation on all test cases
python run_evaluation.py

# Generate HTML report
python run_evaluation.py --report-html

# Run specific category only
python run_evaluation.py --category cultural
```

### 6. Start the Server
```bash
python app.py
```

The server will start on `http://localhost:8000`

### 7. Open in Browser
Navigate to `http://localhost:8000` in your web browser.

## Testing the System

### Manual Testing
1. Open `http://localhost:8000`
2. Type a greeting: "Akkam jirta?"
3. The system should respond in Afaan Oromo
4. Refresh the page - your conversation should persist

### API Testing
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Akkam jirta?", "history": []}'

# List sessions
curl http://localhost:8000/sessions

# Get analytics
curl http://localhost:8000/analytics
```

## Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution**: Make sure you created the `.env` file with your API key.

### Issue: "Module not found" errors
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Rate limit errors
**Solution**: Wait a moment between requests or increase the rate limit in `.env`:
```env
RATE_LIMIT_PER_MINUTE=60/minute
```

### Issue: Database locked
**Solution**: Close any other processes accessing the database:
```bash
rm conversations.db  # Delete and restart (loses data)
```

### Issue: CORS errors in browser
**Solution**: Add your domain to ALLOWED_ORIGINS in `.env`:
```env
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://yourdomain.com
```

## Directory Structure

```
afaan-oromoo-llm/
├── app.py                      # FastAPI application
├── llm_client.py              # LLM client with retry logic
├── database.py                # SQLite database module
├── config.py                  # Configuration management
├── run_evaluation.py          # Evaluation runner
├── index.html                 # Frontend UI
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Test configuration
├── .env                       # Your configuration (create this!)
├── conversations.db           # Database (auto-created)
├── evaluation/
│   ├── __init__.py
│   ├── evaluation.py         # Evaluation metrics
│   ├── test_cases.json       # Test cases
│   └── results/              # Evaluation reports
└── tests/
    ├── __init__.py
    ├── test_llm.py           # LLM tests
    ├── test_database.py      # Database tests
    └── test_api.py           # API tests
```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| GEMINI_API_KEY | (required) | Google Gemini API key |
| MODEL_NAME | gemini-2.5-flash | Model to use |
| TEMPERATURE | 0.7 | Response randomness (0-2) |
| MAX_OUTPUT_TOKENS | 2048 | Maximum response length |
| DATABASE_PATH | conversations.db | SQLite database file |
| HOST | 0.0.0.0 | Server host |
| PORT | 8000 | Server port |
| ALLOWED_ORIGINS | localhost:8000 | CORS allowed origins |
| RATE_LIMIT_PER_MINUTE | 30/minute | API rate limit |
| MAX_INPUT_LENGTH | 2000 | Max input characters |
| MAX_RETRIES | 3 | API retry attempts |

## Advanced Usage

### Custom Evaluation
Create your own test cases in `evaluation/test_cases.json`:
```json
{
  "test_cases": [
    {
      "id": "custom_01",
      "category": "custom",
      "input": "Your test input",
      "expected_type": "response_type",
      "validation": {
        "min_length": 50,
        "max_response_time": 5.0,
        "min_oromo_ratio": 0.3
      }
    }
  ]
}
```

### Database Management
```python
from database import get_database

db = get_database()

# Get total sessions
print(db.get_total_sessions())

# Get analytics
summary = db.get_analytics_summary()
print(summary)

# Clean up old sessions (30+ days)
deleted = db.cleanup_old_sessions(days=30)
print(f"Deleted {deleted} old sessions")
```

### Custom Task Configuration
```python
from config import Config

# Get configuration for different tasks
creative_config = Config.get_generation_config("creative")
factual_config = Config.get_generation_config("factual")
code_config = Config.get_generation_config("code")
```

## Production Deployment

### Before Deploying
1. ✅ Set `ENVIRONMENT=production` in `.env`
2. ✅ Set `DEBUG=false`
3. ✅ Use a production database (PostgreSQL recommended)
4. ✅ Configure proper ALLOWED_ORIGINS
5. ✅ Set up HTTPS
6. ✅ Configure rate limiting appropriately
7. ✅ Set up monitoring and logging
8. ✅ Run security audit

### Recommended Stack
- **Web Server**: Nginx or Apache as reverse proxy
- **ASGI Server**: Uvicorn with multiple workers
- **Database**: PostgreSQL (modify database.py)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or similar

### Example Production Command
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

## Support & Contributing

For issues, improvements, or questions:
1. Check the `IMPLEMENTATION_SUMMARY.md` for details
2. Review test files for usage examples
3. Check console logs for detailed error messages

## License

[Your License Here]

---

**Last Updated**: January 20, 2026
**Version**: 1.0.0 (Phase 1 Complete)

