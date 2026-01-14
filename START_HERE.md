# 🚀 START HERE - Agentic Problem Solver

Welcome! This is your complete, standalone **Agentic Problem Solver** extracted from DeepTutor.

## ⚡ Quick Start (5 minutes)

### 1. Setup Environment
```bash
cp .env.example .env
# Edit .env and add your Google Gemini API key
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Server
```bash
python run_server.py
```

### 4. Test It
```bash
curl -X POST http://localhost:8000/api/solve/direct \
  -H "Content-Type: application/json" \
  -d '{"question": "What is binary search?"}'
```

✅ **Done!** Server is running at `http://localhost:8000`

---

## 📖 Documentation Map

Choose based on your needs:

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [**QUICKSTART.md**](QUICKSTART.md) | Get running in 5 minutes | 5 min |
| [**README.md**](README.md) | Feature overview & examples | 15 min |
| [**SETUP.md**](SETUP.md) | Detailed installation guide | 20 min |
| [**ARCHITECTURE.md**](ARCHITECTURE.md) | System design & technical details | 25 min |
| [**GUIDE.md**](GUIDE.md) | Configuration & customization | 20 min |
| [**PROJECT_SUMMARY.md**](PROJECT_SUMMARY.md) | What was extracted & included | 10 min |

---

## 🎯 Next Steps

### For Immediate Use
1. ✅ Follow **QUICKSTART.md**
2. ✅ Test the API
3. ✅ Try example problems

### For Developers
1. 📖 Read **ARCHITECTURE.md** (understand system design)
2. 📖 Read **GUIDE.md** (customize settings)
3. 🔧 Modify code as needed
4. 🚀 Deploy with Docker

### For DevOps
1. 📖 Read **SETUP.md** (production deployment)
2. 🐳 Run `docker-compose up --build`
3. ⚙️ Configure environment variables
4. 📊 Setup monitoring

---

## 📁 Project Structure

```
agentic-problem-solver/
├── src/
│   ├── agents/solve/          ← Problem solving engine
│   ├── api/                   ← Web API endpoints
│   ├── services/              ← LLM & Config
│   └── logging/               ← Logging setup
│
├── config/
│   └── main.yaml              ← Configuration file
│
├── data/
│   └── user/solve/            ← Output directory
│
├── Documentation/
│   ├── README.md              ← Overview
│   ├── QUICKSTART.md          ← Fast setup
│   ├── SETUP.md               ← Detailed install
│   ├── ARCHITECTURE.md        ← System design
│   ├── GUIDE.md               ← Configuration
│   └── PROJECT_SUMMARY.md     ← Extraction report
│
├── .env.example               ← Environment template
├── requirements.txt           ← Dependencies
├── Dockerfile                 ← Docker image
├── docker-compose.yml         ← Full stack
└── run_server.py              ← Server launcher
```

---

## 🔑 Key Features

✅ **Step-By-Step Solutions** - Breaks problems into logical steps  
✅ **AI-Powered** - Uses GPT-4 Turbo for intelligent solving  
✅ **Real-Time Updates** - WebSocket for live progress  
✅ **Multiple Formats** - JSON + Markdown output  
✅ **Production Ready** - Docker, error handling, logging  
✅ **Fully Documented** - 2500+ lines of guides  

---

## 🧪 Try It Now

### Example 1: Direct HTTP
```bash
curl -X POST http://localhost:8000/api/solve/direct \
  -H "Content-Type: application/json" \
  -d '{"question": "Solve: 3x + 5 = 20"}'
```

### Example 2: WebSocket (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/api/solve');
ws.onopen = () => ws.send(JSON.stringify({
  question: "Explain recursion"
}));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

### Example 3: Python
```python
import asyncio
from src.agents.solve.main_solver import MainSolver

async def main():
    solver = MainSolver()
    result = await solver.solve("Implement bubble sort")
    print(result['final_answer'])

asyncio.run(main())
```

---

## ⚙️ Configuration

### Quick Configuration

Edit **.env**:
```bash
GEMINI_API_KEY=AIzaSy...      # Your Gemini API key
LLM_MODEL=gpt-4-turbo                 # Model to use
API_PORT=8000                         # Server port
MAX_SOLVE_STEPS=5                     # Solution steps
LLM_TEMPERATURE=0.7                   # Randomness (0-1)
```

### Advanced Configuration

Edit **config/main.yaml** for:
- Step count and timeout
- Temperature per agent
- Logging level
- Output directories

See **GUIDE.md** for all options.

---

## 🐳 Docker Deployment

### Single Service
```bash
docker build -t agentic-solver .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=AIzaSy... \
  agentic-solver
```

### Full Stack (with frontend)
```bash
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

---

## 🆘 Troubleshooting

### "API key not found"
```bash
# Ensure .env exists with valid key
ls -la .env
cat .env
```

### "Port 8000 in use"
```bash
# Change port in .env
echo "API_PORT=8001" >> .env
```

### "Module not found"
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### "Connection timeout"
```bash
# Increase timeout
echo "LLM_TIMEOUT=300" >> .env
```

See **SETUP.md** for more troubleshooting.

---

## 🎓 What This Extracts From DeepTutor

**Core Feature**: `src/agents/solve/` - Dual-loop problem solving system

**What's Included**:
- ✅ Problem analysis & step planning
- ✅ Step-by-step solution generation
- ✅ Memory/state management
- ✅ LLM integration
- ✅ WebSocket API
- ✅ Error handling

**What's NOT Included** (intentionally):
- ❌ RAG system (can add if needed)
- ❌ Code execution (can add if needed)
- ❌ Multi-document support
- ❌ Chat history (frontend can implement)

---

## 📚 Documentation at a Glance

**For Everyone**
- Start with **QUICKSTART.md**
- Then read **README.md**

**For Developers**
- Read **ARCHITECTURE.md** (how it works)
- Read **GUIDE.md** (how to customize)

**For DevOps/Deployment**
- Read **SETUP.md** (production setup)
- Use **docker-compose.yml** (easy deployment)

**For Managers/Non-Technical**
- Read **README.md** (features & usage)
- See **PROJECT_SUMMARY.md** (what was built)

---

## ✨ What's New/Improved

| Aspect | Before (DeepTutor) | After (Standalone) |
|--------|-------------------|-------------------|
| Setup Time | Complex | 5 minutes |
| Dependencies | Many systems | Minimal |
| Customization | Difficult | Easy (YAML/Env) |
| Deployment | Complex | Docker ready |
| Documentation | Limited | 2500+ lines |
| Code Organization | Large codebase | Focused module |

---

## 🚀 Get Started NOW!

```bash
# Step 1: Setup (30 seconds)
cp .env.example .env

# Step 2: Configure (1 minute)
# Edit .env, add your API key

# Step 3: Install (2 minutes)
pip install -r requirements.txt

# Step 4: Run (1 second)
python run_server.py

# Step 5: Test (immediate)
curl http://localhost:8000/health
```

**Total: ~5 minutes to full working system!**

---

## 💡 First Problem to Try

```bash
# After server is running:

curl -X POST http://localhost:8000/api/solve/direct \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain how the Fibonacci sequence works and write pseudocode for it"
  }'
```

You'll get back a detailed, step-by-step solution! 🎉

---

## 📞 Need Help?

1. **Quick questions?** → Check **QUICKSTART.md**
2. **Setup issues?** → Check **SETUP.md** troubleshooting
3. **Want to customize?** → Read **GUIDE.md**
4. **Understanding system?** → Read **ARCHITECTURE.md**
5. **Everything?** → See **README.md**

---

## ✅ Verification Checklist

Before considering setup complete, verify:

- [ ] `.env` file created with API key
- [ ] `pip install -r requirements.txt` completed
- [ ] `python run_server.py` starts without errors
- [ ] `curl http://localhost:8000/health` returns 200
- [ ] One test problem solved successfully

✅ **All checked?** You're ready to go! 🚀

---

**Status**: ✅ **Production Ready**  
**Version**: 1.0.0  
**Last Updated**: January 2024  

---

<div align="center">

### Ready to Solve Problems?

[📖 Read QUICKSTART](QUICKSTART.md) | [🏗️ Read ARCHITECTURE](ARCHITECTURE.md) | [⚙️ Read GUIDE](GUIDE.md)

**Happy Problem Solving! 🎉**

</div>
