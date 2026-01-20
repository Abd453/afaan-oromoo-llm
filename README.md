# Afaan Oromoo Conversational AI System

A production-ready conversational AI system specialized in **Afaan Oromoo** (Oromo language) with English code-switching support, built using Google's Gemini 2.5 Flash model. This system provides culturally-aware responses, persistent conversation history, comprehensive evaluation metrics, and robust error handling.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Main Functionalities](#main-functionalities)
- [Language & LLM Details](#language--llm-details)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
- [Limitations](#limitations)
- [Evaluation & Testing](#evaluation--testing)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## 🌍 Overview

The **Afaan Oromoo Conversational AI System** is designed to bridge the technological gap for Oromo language speakers by providing an intelligent, context-aware chatbot that understands and responds in Afaan Oromoo. The system is culturally sensitive, handles technical queries, educational content, and daily conversations while maintaining linguistic accuracy.

### Why Afaan Oromoo?

- **Speakers**: ~40 million native speakers (Ethiopia, Kenya)
- **Language Family**: Cushitic branch of Afro-Asiatic languages
- **Digital Gap**: Limited AI/NLP resources available
- **Cultural Importance**: Official language of Oromia Region, Ethiopia

---

## 🚀 Main Functionalities

### 1. **Conversational AI**
- Natural language understanding in Afaan Oromoo
- Context-aware responses maintaining conversation history
- Support for greetings, questions, technical discussions, and educational queries
- Code-switching between Afaan Oromoo and English

### 2. **Session Management**
- Persistent conversation history across page refreshes
- Multiple conversation sessions with titles
- Session creation, retrieval, update, and deletion
- Automatic session recovery on page load

### 3. **Database Persistence**
- SQLite-based storage for conversations
- Message history preservation
- Analytics tracking (response times, error rates)
- Session metadata management

### 4. **Evaluation Framework**
- Comprehensive test suite with 22+ test cases
- Automated quality metrics:
  - Language consistency (% Afaan Oromoo content)
  - Response time measurement
  - Cultural sensitivity scoring
  - Error detection
- HTML and JSON report generation
- Category-based testing (greetings, technical, cultural, etc.)

### 5. **Error Handling & Reliability**
- Exponential backoff retry mechanism (up to 3 attempts)
- Intelligent error classification (rate limits, API errors, network issues)
- Graceful degradation on failures
- User-friendly error messages in Afaan Oromoo

### 6. **Security Features**
- Rate limiting (30 requests/minute default)
- Input validation (max 2000 characters)
- CORS configuration for secure cross-origin requests
- Environment-based configuration
- Request size limits

### 7. **Web Interface**
- Modern, responsive UI with dark theme
- Mobile-friendly design
- Real-time chat with typing indicators
- Code syntax highlighting
- LaTeX/Math rendering support
- Markdown formatting
- Message editing and regeneration

### 8. **Analytics & Monitoring**
- Usage statistics tracking
- Response time analytics
- Error logging and reporting
- Query type categorization
- Performance metrics dashboard

---

## 🗣️ Language & LLM Details

### Primary Language: **Afaan Oromoo**

**Linguistic Features:**
- **Writing System**: Latin script (Qubee)
- **Phonology**: Rich vowel system with distinctive sounds
- **Grammar**: Subject-Object-Verb (SOV) word order
- **Characteristics**: Agglutinative morphology
- **Dialects**: Western, Eastern, Southern variants (system handles mixed input)

**Cultural Context Integration:**
- Recognition of Oromo cultural concepts (Gada system, Irreecha, Odaa)
- Awareness of traditional practices and social norms
- Respectful language and honorifics
- Historical and geographical knowledge of Oromia

**Code-Switching Support:**
- Seamless handling of mixed Afaan Oromoo-English input
- Technical terms explained in both languages
- Adaptive response language based on user query

### LLM: **Google Gemini 2.5 Flash**

**Model Specifications:**
- **Provider**: Google AI (via `google-generativeai` package)
- **Model Name**: `gemini-2.5-flash`
- **Model Type**: Large Language Model with multimodal capabilities
- **Context Window**: Extended context support
- **Generation Parameters**:
  - Temperature: 0.7 (balanced creativity)
  - Max Output Tokens: 2048 (increased for detailed responses)
  - Top-P: 0.95 (nucleus sampling)
  - Top-K: 40 (token diversity)

**Why Gemini 2.5 Flash?**
- ✅ Fast response times (<3 seconds average)
- ✅ Strong multilingual capabilities
- ✅ Context-aware conversation handling
- ✅ Cost-effective for production use
- ✅ Regular updates and improvements
- ✅ Excellent at code generation and technical explanations

**System Instructions:**
The model is fine-tuned via system prompts to:
- Prioritize Afaan Oromoo in responses
- Maintain cultural sensitivity and awareness
- Handle code-switching appropriately
- Provide educational, patient responses
- Use respectful language and honorifics
- Be honest about knowledge limitations

**Task-Specific Configurations:**
| Task Type | Temperature | Max Tokens | Use Case |
|-----------|-------------|------------|----------|
| Default | 0.7 | 2048 | General conversation |
| Creative | 0.9 | 2048 | Stories, poems, creative writing |
| Factual | 0.3 | 1024 | Historical facts, definitions |
| Translation | 0.5 | 1536 | Language translation tasks |
| Code | 0.4 | 2048 | Programming assistance |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (HTML/JS)                   │
│  • Modern responsive UI with dark theme                  │
│  • Real-time chat interface                              │
│  • Session management sidebar                            │
│  • LocalStorage for session persistence                  │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP/REST API
┌──────────────────▼──────────────────────────────────────┐
│                  FastAPI Backend (app.py)                │
│  • RESTful API endpoints                                 │
│  • Rate limiting & input validation                      │
│  • CORS configuration                                    │
│  • Request/response handling                             │
└──────┬──────────────────────┬─────────────────┬─────────┘
       │                      │                 │
       ▼                      ▼                 ▼
┌──────────────┐    ┌──────────────────┐  ┌──────────┐
│  LLM Client  │    │    Database      │  │  Config  │
│  (Gemini)    │    │    (SQLite)      │  │  Module  │
│              │    │                  │  │          │
│ • Retry      │    │ • Sessions       │  │ • Env    │
│   logic      │    │ • Messages       │  │   vars   │
│ • Error      │    │ • Analytics      │  │ • Valid. │
│   handling   │    │                  │  │          │
└──────────────┘    └──────────────────┘  └──────────┘

┌─────────────────────────────────────────────────────────┐
│              Evaluation Framework                        │
│  • Test suite (22+ cases)                                │
│  • Metrics calculation                                   │
│  • Report generation (HTML/JSON)                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                Testing Infrastructure                     │
│  • Unit tests (60+ test cases)                           │
│  • Integration tests                                      │
│  • API endpoint tests                                     │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### For Users
- 🗣️ **Natural Conversation**: Chat naturally in Afaan Oromoo
- 💾 **Persistent History**: Conversations saved automatically
- 📱 **Mobile Friendly**: Works seamlessly on phones and tablets
- 🎨 **Beautiful UI**: Modern dark theme with smooth animations
- ⚡ **Fast Responses**: Average response time <3 seconds
- 🔄 **Session Management**: Multiple conversations, easy switching

### For Developers
- 🧪 **Comprehensive Testing**: 60+ unit and integration tests
- 📊 **Evaluation Metrics**: Automated quality assessment
- 🔧 **Modular Architecture**: Easy to extend and maintain
- 📝 **Well Documented**: Extensive documentation and examples
- 🐛 **Error Handling**: Robust retry logic and graceful failures
- 🔒 **Security First**: Rate limiting, input validation, CORS

### For Researchers
- 📈 **Analytics Dashboard**: Track usage patterns and performance
- 🎯 **Evaluation Framework**: Measure system quality objectively
- 📊 **Metrics Tracking**: Language consistency, response times, errors
- 🧬 **Test Dataset**: 22 curated test cases for benchmarking
- 📄 **Report Generation**: HTML/JSON reports with visualizations

---

## 💻 Installation

### Prerequisites
- Python 3.9 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Git (for cloning)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/afaan-oromoo-llm.git
cd afaan-oromoo-llm
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_api_key_here
MAX_OUTPUT_TOKENS=2048
TEMPERATURE=0.7
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
DATABASE_PATH=conversations.db
RATE_LIMIT_PER_MINUTE=30/minute
```

4. **Run tests** (optional but recommended)
```bash
pytest -v
```

5. **Start the server**
```bash
python app.py
```

6. **Open in browser**
Navigate to `http://localhost:8000`

📖 **For detailed setup instructions**, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## 🎯 Usage

### Basic Chat
```python
# The web interface handles this automatically, but programmatically:
from llm_client import query_llm

response = query_llm("Akkam jirta?")
print(response)  # Output in Afaan Oromoo
```

### With Conversation History
```python
history = [
    {"role": "user", "parts": ["Maal hojjechaa jirta?"]},
    {"role": "model", "parts": ["Ani si gargaaraa jira..."]}
]

response = query_llm("Barnoota waa'ee AI naaf ibsi", history_input=history)
```

### Using the API
```bash
# Send a chat message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Akkam jirta?",
    "history": []
  }'

# Create a session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-123",
    "title": "My Conversation"
  }'

# Get analytics
curl http://localhost:8000/analytics
```

### Running Evaluations
```bash
# Run all tests
python run_evaluation.py

# Run specific category
python run_evaluation.py --category cultural

# Generate HTML report
python run_evaluation.py --report-html
```

---

## ⚠️ Limitations

### Language Limitations

1. **Dialect Variations**
   - System trained primarily on standard written Afaan Oromoo
   - Regional dialects (Western, Eastern, Southern) may have varying accuracy
   - Colloquial expressions might not always be understood perfectly

2. **Vocabulary Coverage**
   - Technical terms in Afaan Oromoo may be limited
   - Newer technology terms often rely on English loanwords
   - Specialized domain knowledge (medical, legal) may be less comprehensive

3. **Code-Switching**
   - While supported, heavy code-switching may reduce response quality
   - Complex mixed-language queries may be interpreted inconsistently

### Technical Limitations

1. **LLM-Based Constraints**
   - Responses generated by AI may contain factual errors
   - Cultural knowledge limited to training data
   - Cannot access real-time information or external databases
   - May occasionally "hallucinate" or provide incorrect information

2. **Context Window**
   - Long conversations (20+ exchanges) automatically truncated
   - Very long inputs (>2000 characters) are rejected
   - Context may be lost in extended sessions

3. **Performance**
   - Response time depends on Google API availability (typically <3s)
   - Rate limiting: 30 requests/minute (configurable)
   - API quota limitations from Google Cloud

4. **Accuracy Metrics** (From Evaluation)
   - Average Afaan Oromoo consistency: ~60-70% (varies by query type)
   - Technical queries may mix English and Oromoo
   - Cultural questions show higher language consistency (70-80%)

### Cultural Limitations

1. **Cultural Nuances**
   - System may not capture all regional cultural variations
   - Traditional knowledge representation may be simplified
   - Proverbs and idioms may not always be interpreted correctly

2. **Respect and Etiquette**
   - While programmed to be respectful, may not capture all social nuances
   - Age-based honorifics may not always be applied appropriately

### Infrastructure Limitations

1. **API Dependency**
   - Requires active internet connection
   - Dependent on Google Gemini API availability
   - API key must be valid and have quota

2. **Storage**
   - SQLite database suitable for <100k messages
   - For production scale, PostgreSQL recommended
   - No built-in data backup system

3. **Security**
   - Basic rate limiting (IP-based, proxy limitations)
   - No built-in user authentication system
   - CORS must be configured for production deployment

### Known Issues

1. **Package Deprecation**
   - `google-generativeai` package is deprecated
   - Migration to `google-genai` needed (Phase 2)
   - See [DEPRECATION_NOTICE.md](DEPRECATION_NOTICE.md)

2. **Windows Compatibility**
   - Unicode display issues in some Windows terminals (fixed with ASCII markers)
   - Database file locking in concurrent scenarios

3. **Mobile Safari**
   - LaTeX rendering may have slight layout issues
   - Virtual keyboard may obscure input field

---

## 🧪 Evaluation & Testing

### Automated Evaluation

The system includes a comprehensive evaluation framework:

```bash
# Run full evaluation suite (22 test cases)
python run_evaluation.py

# Generate detailed HTML report
python run_evaluation.py --report-html

# Test specific category
python run_evaluation.py --category greetings
```

### Test Categories
- **Greetings** (2 tests): Basic conversational openings
- **Technical** (3 tests): Programming, engineering questions
- **Cultural** (3 tests): Oromo culture, traditions, history
- **Mixed Language** (2 tests): Code-switching scenarios
- **Conversational** (2 tests): General dialogue
- **Mathematical** (2 tests): Math problems and theorems
- **Educational** (2 tests): Science, learning content
- **Edge Cases** (3 tests): Empty input, very long text
- **Historical** (1 test): Historical inquiries
- **Practical** (1 test): Daily life advice
- **Translation** (1 test): Language translation

### Evaluation Metrics
- ✅ **Language Consistency**: % of Afaan Oromoo in response
- ✅ **Response Time**: Latency measurement
- ✅ **Cultural Markers**: Oromo-specific term detection
- ✅ **Error Rate**: Failed requests tracking
- ✅ **Quality Scoring**: Pass/fail criteria (80% threshold)

### Unit Tests
```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_llm.py -v
pytest tests/test_database.py -v
pytest tests/test_api.py -v

# With coverage
pytest --cov=. tests/
```

**Test Coverage**: 60+ test cases covering:
- LLM client functionality
- Database operations
- API endpoints
- Error handling
- Input validation

---

## 📚 API Documentation

### Endpoints

#### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "user_input": "Akkam jirta?",
  "history": [],
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "status": "success",
  "response": "Nagaan jira! Si gargaaruu danda'a?",
  "response_time": 1.23
}
```

#### Session Management

**Create Session**
```http
POST /sessions
{
  "session_id": "sess-123",
  "title": "My Conversation"
}
```

**List Sessions**
```http
GET /sessions?limit=50&offset=0
```

**Get Session**
```http
GET /sessions/{session_id}
```

**Update Session**
```http
PUT /sessions/{session_id}
{
  "title": "Updated Title"
}
```

**Delete Session**
```http
DELETE /sessions/{session_id}
```

#### Analytics
```http
GET /analytics?start_date=2026-01-01&end_date=2026-12-31
```

For detailed API documentation, see [API.md](API.md) or visit `http://localhost:8000/docs` when running.

---

## 📁 Project Structure

```
afaan-oromoo-llm/
├── app.py                      # FastAPI application & API endpoints
├── llm_client.py              # LLM client with retry logic & error handling
├── database.py                # SQLite database manager
├── config.py                  # Configuration management
├── run_evaluation.py          # Evaluation runner CLI
├── index.html                 # Frontend web interface
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Test configuration
├── .env                       # Environment variables (create this!)
├── .gitignore                 # Git ignore patterns
│
├── evaluation/                # Evaluation framework
│   ├── __init__.py
│   ├── evaluation.py         # Metrics & scoring logic
│   ├── test_cases.json       # Test dataset (22 cases)
│   └── results/              # Evaluation reports
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_llm.py           # LLM client tests
│   ├── test_database.py      # Database tests
│   └── test_api.py           # API integration tests
│
└── docs/                      # Documentation
    ├── README.md             # This file
    ├── SETUP_GUIDE.md        # Detailed setup instructions
    ├── IMPLEMENTATION_SUMMARY.md  # Technical implementation details
    ├── CHANGES.md            # Change log
    └── DEPRECATION_NOTICE.md # Package deprecation info
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Areas for Contribution

1. **Language Resources**
   - Expand Afaan Oromoo test cases
   - Add dialect-specific examples
   - Contribute cultural knowledge base
   - Improve translation pairs

2. **Technical Improvements**
   - Migrate to `google-genai` package
   - Add voice input/output
   - Implement multi-modal support (images)
   - Enhance evaluation metrics

3. **Testing**
   - Add more test cases
   - Improve test coverage
   - Performance benchmarking
   - Cross-platform testing

4. **Documentation**
   - Translate docs to Afaan Oromoo
   - Add tutorials and examples
   - Create video guides
   - Improve API documentation

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest -v`)
5. Run evaluation (`python run_evaluation.py`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards
- Follow PEP 8 style guide
- Add type hints where applicable
- Write unit tests for new features
- Update documentation
- Ensure all tests pass

---

## 📊 Research & Citation

If you use this system in your research, please cite:

```bibtex
@software{afaan_oromoo_llm_2026,
  title = {Afaan Oromoo Conversational AI System},
  author = {Your Name},
  year = {2026},
  url = {https://github.com/yourusername/afaan-oromoo-llm},
  note = {A production-ready conversational AI system for Afaan Oromoo using Google Gemini 2.5 Flash}
}
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Oromo Language Community**: For linguistic guidance and cultural insights
- **Google AI**: For providing the Gemini API
- **Open Source Community**: For tools and frameworks (FastAPI, pytest, etc.)
- **Contributors**: All those who help improve this system

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/afaan-oromoo-llm/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/afaan-oromoo-llm/discussions)
- **Email**: your.email@example.com

---

## 🗺️ Roadmap

### Phase 2 (Future)
- [ ] Migrate to `google-genai` package
- [ ] Voice input/output support
- [ ] Multi-modal capabilities (image understanding)
- [ ] Analytics dashboard UI
- [ ] User authentication system
- [ ] PostgreSQL migration for scalability

### Phase 3 (Long-term)
- [ ] Retrieval-Augmented Generation (RAG) with Oromo corpus
- [ ] Fine-tuning on Oromo-specific datasets
- [ ] Mobile applications (iOS/Android)
- [ ] Offline mode support
- [ ] Community knowledge base
- [ ] Multi-dialect support

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ for the Oromo community**

*Galata! Thank you for using the Afaan Oromoo Conversational AI System.*

