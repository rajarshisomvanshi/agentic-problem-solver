# Quick Start Guide - Agentic Problem Solver

Get up and running in 5 minutes!

## Step 1: Setup (2 minutes)

### Clone/Enter Project
```bash
cd ~/Desktop/agentic-problem-solver
```

### Configure API Key
```bash
# Copy template
cp .env.example .env

# Edit .env with your OpenAI API key
# Open .env and replace: GEMINI_API_KEY=your-api-key-here
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Start Server (1 minute)

```bash
python run_server.py
```

You should see:
```
🚀 Starting Agentic Problem Solver API
   Host: 0.0.0.0
   Port: 8000
   Environment: development
   Reload: True
```

## Step 3: Test It (2 minutes)

### Option A: Simple HTTP Request
```bash
curl -X POST http://localhost:8000/api/solve/direct \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the Fibonacci sequence?"}'
```

### Option B: Using Python
```python
import asyncio
from src.agents.solve.main_solver import MainSolver

async def main():
    solver = MainSolver()
    result = await solver.solve("Explain the binary search algorithm")
    print("✅ Solution:", result['final_answer'])

asyncio.run(main())
```

### Option C: WebSocket (Real-time)
```javascript
// In browser console or Node.js
const ws = new WebSocket('ws://localhost:8000/api/solve');

ws.onopen = () => {
  ws.send(JSON.stringify({
    question: "How do I solve a quadratic equation?"
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === 'progress') {
    console.log('Progress:', msg.data);
  }
  if (msg.type === 'result') {
    console.log('Final Answer:', msg.data.final_answer);
  }
};
```

## Try These Example Problems

1. **Math**: "Solve 3x + 5 = 20"
2. **Physics**: "Calculate velocity after 5 seconds with v₀=10 m/s, a=2 m/s²"
3. **Coding**: "Implement bubble sort algorithm"
4. **Chemistry**: "Balance: C + O₂ → CO₂"
5. **Logic**: "Explain Boolean algebra"

## Output

Solutions are saved to: `./data/user/solve/solve_YYYYMMDD_HHMMSS/`

Files:
- `final_answer.md` - Markdown formatted solution
- `solve_chain.json` - JSON with all steps
- `result.json` - Summary

## Docker Quick Start

```bash
# Build and run
docker-compose up --build

# Access:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:3000
```

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🏗️ Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- ⚙️ See [SETUP.md](docs/SETUP.md) for detailed installation
- 🎯 Read [GUIDE.md](docs/GUIDE.md) for configuration options

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Ensure `.env` file exists with valid key |
| "Port 8000 in use" | Change API_PORT in `.env` |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Connection refused" | Ensure server is running (step 2) |

## Support

- 📧 See README.md for contact info
- 🐛 Check GitHub Issues
- 📚 Review documentation files

**Happy problem-solving! 🚀**
