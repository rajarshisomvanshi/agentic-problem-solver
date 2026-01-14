# Agentic Problem Solver

Intelligent step-by-step problem solver powered by AI agents. Upload problems (math, coding, physics, etc.) and receive detailed, AI-generated solutions with clear reasoning at each step.

## 🌟 Features

- **📋 Step-by-Step Solutions**: Problems broken down into logical, executable steps
- **🤖 AI-Powered Reasoning**: Uses GPT-4 Turbo for intelligent problem analysis
- **⚡ Real-Time Progress**: WebSocket streaming of solving progress
- **🎯 Multiple Problem Types**: Math, coding, physics, chemistry, and more
- **📊 Detailed Output**: Structured JSON + markdown formats
- **🐳 Docker Support**: Easy deployment with Docker and docker-compose
- **🔄 Async Processing**: Efficient async/await architecture
- **📁 Persistent Storage**: Solutions saved for later reference

## 🏗️ Architecture

```
User Input (Problem/Question)
        ↓
    MainSolver
        ↓
    ├─ Planning Phase (Generate solution steps)
    ├─ Solving Phase (Execute each step with LLM)
    └─ Formatting Phase (Generate final answer)
        ↓
   Structured Output (Steps + Final Answer + Citations)
```

### Components

- **Backend**: FastAPI + async Python for real-time problem solving
- **LLM Integration**: OpenAI GPT-4 Turbo for intelligent reasoning
- **WebSocket**: Real-time progress streaming to frontend
- **Memory System**: Persistent solve-chain storage (JSON)
- **Configuration**: YAML-based config + environment variables
- **Frontend**: Next.js ready (structure provided)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key
- Node.js 18+ (for frontend, optional)

### Installation

1. **Clone/Create project**:
```bash
cd ~/Desktop
# Project already created at: agentic-problem-solver
```

2. **Setup environment**:
```bash
cd agentic-problem-solver
cp .env.example .env
# Edit .env with your OpenAI API key
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run server**:
```bash
python run_server.py
```

Server starts at: `http://localhost:8000`

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build
```

Access at:
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## 📖 API Usage

### WebSocket Endpoint: `/api/solve`

**Connect and send problem**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/solve');

ws.onopen = () => {
  ws.send(JSON.stringify({
    question: "How do I implement binary search?",
    problem: "Alternative field name"
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  if (msg.type === 'progress') {
    // Update UI with progress
    console.log(msg.event, msg.data);
  }
  
  if (msg.type === 'result') {
    // Display final result
    console.log(msg.data.final_answer);
  }
  
  if (msg.type === 'error') {
    console.error(msg.message);
  }
};
```

### HTTP Endpoint: `POST /api/solve/direct` (Non-streaming)

```bash
curl -X POST http://localhost:8000/api/solve/direct \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Solve: 2x + 5 = 15"
  }'
```

Response:
```json
{
  "success": true,
  "result": {
    "task_id": "solve_12345",
    "question": "Solve: 2x + 5 = 15",
    "final_answer": "Detailed solution...",
    "steps": 4,
    "output_dir": "./data/user/solve/solve_20240114_120000"
  }
}
```

## 📁 Project Structure

```
agentic-problem-solver/
├── src/
│   ├── agents/
│   │   └── solve/
│   │       ├── main_solver.py          # Main orchestration
│   │       ├── memory/
│   │       │   └── solve_memory.py     # State management
│   │       ├── solve_loop/             # Solution execution
│   │       ├── analysis_loop/          # Problem analysis
│   │       └── utils/
│   │
│   ├── api/
│   │   ├── main.py                     # FastAPI app
│   │   ├── routers/
│   │   │   └── solve.py               # API endpoints
│   │   └── utils/
│   │
│   ├── services/
│   │   ├── llm.py                      # LLM configuration
│   │   └── config.py                   # Configuration loader
│   │
│   └── logging/
│       └── handlers/
│
├── config/
│   └── main.yaml                       # Application config
│
├── data/
│   └── user/
│       └── solve/                      # Solution outputs
│
├── web/                                # Frontend (Next.js)
│
├── .env.example                        # Environment template
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Project metadata
├── Dockerfile                          # Container image
├── docker-compose.yml                  # Multi-container setup
├── run_server.py                       # Server launcher
└── README.md                           # This file
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# OpenAI API
GEMINI_API_KEY=AIzaSy...
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo

# Server
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
DEBUG=true
```

### YAML Configuration (config/main.yaml)

Edit `config/main.yaml` to customize:
- Max steps for solution
- LLM temperature and token limits
- Logging level
- Output directories

## 🧪 Testing

### Test with curl

```bash
# Simple test
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Status endpoint
curl http://localhost:8000/api/status

# Solve (direct HTTP)
curl -X POST http://localhost:8000/api/solve/direct \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the Fibonacci sequence?"}'
```

### Test with Python

```python
import asyncio
from src.agents.solve.main_solver import MainSolver

async def test():
    solver = MainSolver()
    result = await solver.solve("Explain recursion in programming")
    print(result['final_answer'])

asyncio.run(test())
```

## 📝 Output Format

Solutions are saved in two formats:

**1. Markdown** (`final_answer.md`):
```markdown
# Solution to: Your Question

## Step 1: Initial Analysis
[Content]

## Step 2: Core Approach
[Content]

## Step 3: Implementation
[Content]

## Step 4: Verification
[Content]
```

**2. JSON** (`solve_chain.json`):
```json
{
  "task_id": "solve_...",
  "user_question": "...",
  "solve_chains": [
    {
      "step_id": "s001",
      "step_target": "...",
      "step_response": "...",
      "status": "done",
      "tool_calls": []
    }
  ],
  "metadata": {
    "total_steps": 4,
    "completed_steps": 4,
    "total_tool_calls": 0
  }
}
```

## 🔧 Troubleshooting

### "GEMINI_API_KEY not provided"
- Ensure `.env` file exists with valid API key
- Run: `export GEMINI_API_KEY=AIzaSy...`

### Server won't start
- Check if port 8000 is available
- Verify all dependencies: `pip install -r requirements.txt`
- Check logs: `tail -f logs/*.log`

### WebSocket connection fails
- Ensure backend is running on correct port
- Check CORS settings in `src/api/main.py`
- Verify firewall allows WebSocket connections

### LLM rate limits
- Increase timeout in `.env`: `LLM_TIMEOUT=300`
- Reduce max tokens: `LLM_MAX_TOKENS=2000`
- Implement request queuing for batch operations

## 📚 Examples

### Example 1: Math Problem
```
Question: Solve the quadratic equation: x² + 5x + 6 = 0
Steps:
1. Identify equation form
2. Apply quadratic formula
3. Calculate discriminant
4. Find solutions
5. Verify answers
```

### Example 2: Coding Problem
```
Question: Implement a function to check if a string is a palindrome
Steps:
1. Define palindrome concept
2. Algorithm approach
3. Code implementation
4. Handle edge cases
5. Test with examples
```

### Example 3: Physics Problem
```
Question: Calculate velocity after 5 seconds if initial velocity is 10 m/s and acceleration is 2 m/s²
Steps:
1. Identify given values
2. State kinematic equation
3. Substitute values
4. Calculate result
5. Verify units and reasonableness
```

## 🚀 Deployment

### AWS Lambda + API Gateway
See [DEPLOYMENT_AWS.md](docs/deployment/aws.md)

### Google Cloud Run
See [DEPLOYMENT_GCP.md](docs/deployment/gcp.md)

### Self-Hosted
```bash
# Using systemd
sudo systemctl start agentic-solver

# Using supervisor
supervisorctl start agentic-solver

# Using PM2
pm2 start run_server.py
```

## 📦 Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **openai**: LLM API client
- **pydantic**: Data validation
- **PyYAML**: Configuration management
- **python-dotenv**: Environment variables

## 🤝 Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Add tests
4. Submit pull request

## 📄 License

MIT License - see LICENSE file

## 🎯 Roadmap

- [ ] Support for multiple LLM providers (Claude, Llama, etc.)
- [ ] Interactive step refinement
- [ ] Solution caching and retrieval
- [ ] Batch problem processing
- [ ] Advanced visualization of solution steps
- [ ] Integration with document databases
- [ ] Mobile app (React Native)
- [ ] Problem difficulty estimation

## 📧 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@example.com

## 🙏 Acknowledgments

Built with inspiration from DeepTutor's dual-loop problem-solving architecture.

---

**Made with ❤️ for learners and problem-solvers everywhere**
