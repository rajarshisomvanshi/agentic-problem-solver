# Installation & Setup Guide

Complete installation instructions for Agentic Problem Solver.

## Prerequisites

### System Requirements
- OS: Windows, macOS, Linux
- Python: 3.10 or higher
- RAM: 4GB minimum (8GB recommended)
- Disk: 2GB free space

### Required Accounts
- OpenAI API account with GPT-4 Turbo access (or compatible LLM)
- Internet connection for API calls

## Full Installation

### 1. Clone/Navigate to Project

```bash
cd ~/Desktop
# Project is at: ./agentic-problem-solver
cd agentic-problem-solver
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Setup Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env file - Add your Google Gemini API key
# On Windows:
notepad .env

# On macOS/Linux:
nano .env
```

**Required fields in .env**:
```
GEMINI_API_KEY=AIzaSy...
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo
```

**Optional fields**:
```
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai` - LLM API client
- `pydantic` - Data validation
- `PyYAML` - Config management
- Plus other supporting libraries

### 5. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10+

# Check pip packages
pip list | grep fastapi
pip list | grep openai
pip list | grep uvicorn

# Test import
python -c "from src.agents.solve.main_solver import MainSolver; print('✅ Import successful')"
```

## Running the Server

### Method 1: Direct Python

```bash
python run_server.py
```

Output:
```
🚀 Starting Agentic Problem Solver API
   Host: 0.0.0.0
   Port: 8000
   Environment: development
   Reload: True
INFO:     Started server process [1234]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Method 2: Using Uvicorn Directly

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Method 3: Using Docker

```bash
docker build -t agentic-solver .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=AIzaSy... \
  agentic-solver
```

### Method 4: Using Docker Compose

```bash
docker-compose up --build
```

## Configuration

### Configure via .env

```bash
# LLM Settings
GEMINI_API_KEY=AIzaSy...
LLM_MODEL=gpt-4-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000

# Server Settings
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production
DEBUG=false

# Logging
LOG_LEVEL=INFO
LOG_DIR=./data/user/logs
```

### Configure via YAML

Edit `config/main.yaml`:

```yaml
solve:
  max_steps: 5
  max_retries: 2
  timeout: 300

llm:
  model: "gpt-4-turbo"
  temperature: 0.7
  max_tokens: 4000

logging:
  level: "INFO"
  console_output: true
  save_to_file: true
```

## Verify Setup

### Health Check

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "agentic-problem-solver"}
```

### Test Endpoint

```bash
curl http://localhost:8000/
# Shows API information
```

### Solve Endpoint

```bash
curl -X POST http://localhost:8000/api/solve/direct \
  -H "Content-Type: application/json" \
  -d '{"question": "What is 2+2?"}'
```

## Troubleshooting

### Problem: "ModuleNotFoundError"

**Solution**:
```bash
# Ensure you're in virtual environment
activate venv  # or source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify project root
python -c "import sys; print(sys.path)"
```

### Problem: "GEMINI_API_KEY not found"

**Solution**:
```bash
# Verify .env file exists
ls -la .env  # or dir .env on Windows

# Check file contents
cat .env

# Ensure key is set (no trailing spaces)
GEMINI_API_KEY=AIzaSy...  # No comments after key
```

### Problem: "Port 8000 already in use"

**Solution**:
```bash
# Change port in .env
echo "API_PORT=8001" >> .env

# Or use docker on different port
docker-compose up -p 8001:8000
```

### Problem: "Connection timeout to OpenAI"

**Solution**:
```bash
# Increase timeout
echo "LLM_TIMEOUT=300" >> .env

# Check internet connection
ping api.openai.com

# Try with different base URL
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Problem: "Out of memory"

**Solution**:
```bash
# Reduce token limits
LLM_MAX_TOKENS=2000

# Reduce concurrent requests
# Edit config/main.yaml: max_steps: 3
```

## Development Setup

### Install Development Tools

```bash
pip install -r requirements-dev.txt  # If it exists
# Or manually:
pip install pytest pytest-asyncio black ruff mypy
```

### Code Formatting

```bash
# Format code
black src/

# Check linting
ruff check src/

# Type checking
mypy src/
```

### Running Tests

```bash
pytest tests/
pytest tests/ -v  # Verbose
pytest tests/ --asyncio-mode=auto  # For async tests
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Update `.env` with production settings
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Use strong API keys
- [ ] Setup SSL/TLS certificate
- [ ] Configure firewall rules
- [ ] Setup log rotation
- [ ] Configure backup strategy

### Using Gunicorn (Production)

```bash
pip install gunicorn

gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  src.api.main:app
```

### Using Systemd (Linux)

Create `/etc/systemd/system/agentic-solver.service`:

```ini
[Unit]
Description=Agentic Problem Solver
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/agentic-solver
Environment="PATH=/opt/agentic-solver/venv/bin"
ExecStart=/opt/agentic-solver/venv/bin/python run_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable agentic-solver
sudo systemctl start agentic-solver
sudo systemctl status agentic-solver
```

## Next Steps

1. ✅ Installation complete!
2. 📖 Read [QUICKSTART.md](QUICKSTART.md)
3. 🏗️ Learn about [ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. 📝 Explore [examples/](examples/)
5. 🚀 Deploy to production

## Support & Issues

- 📚 Check README.md
- 🐛 Report issues on GitHub
- 📧 Contact support (see README.md)

---

**Ready to solve problems? 🚀**
