# System Architecture

Complete technical architecture of Agentic Problem Solver.

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│              (WebSocket client, UI rendering)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ WebSocket /api/solve
                         │ or HTTP POST /api/solve/direct
                         ▼
        ┌────────────────────────────────────┐
        │   FastAPI Application Server       │
        │   (WebSocket handler, routing)     │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────────────┐
        │        MainSolver (Orchestrator)            │
        │   ├─ Phase 1: Planning                      │
        │   ├─ Phase 2: Solving (Step execution)      │
        │   └─ Phase 3: Formatting                    │
        └─────────────┬───────────────────────────────┘
                      │
        ┌─────────────┴─────────────┬──────────────────┐
        │                           │                  │
        ▼                           ▼                  ▼
    ┌────────────┐         ┌──────────────┐    ┌────────────┐
    │ LLM Client │         │ Memory Store │    │ Config Mgr │
    │ (OpenAI)   │         │ (SolveMemory)│    │ (YAML/Env) │
    └────────────┘         └──────────────┘    └────────────┘
```

## Component Details

### 1. Frontend Layer (Next.js)

**Location**: `web/`

**Responsibilities**:
- User interface for problem input
- Real-time progress display
- Solution rendering and formatting
- WebSocket connection management

**Key Features**:
- Problem upload/text input
- Live progress tracking
- Step-by-step visualization
- Solution export (PDF, Markdown)

### 2. API Layer (FastAPI)

**Location**: `src/api/`

**Key Files**:
- `main.py` - FastAPI application setup
- `routers/solve.py` - Problem solving endpoints

**Endpoints**:
```python
GET  /health              # Health check
GET  /                    # API info
GET  /api/status          # Service status
POST /api/solve/direct    # Direct HTTP solving
WS   /api/solve          # WebSocket solving
```

**CORS Settings**:
- Allows all origins (can be restricted in production)
- Supports credentials
- All HTTP methods

### 3. Agent Layer

**Location**: `src/agents/solve/`

#### MainSolver
**File**: `main_solver.py`

**Workflow**:
1. **Planning Phase**
   - Analyzes user problem
   - Generates logical solution steps
   - Creates SolveMemory with step structure

2. **Solving Phase**
   - Iterates through each step
   - Calls LLM to generate step content
   - Updates memory with results
   - Sends progress updates

3. **Formatting Phase**
   - Aggregates all step responses
   - Generates polished final answer
   - Saves results to file

**Key Methods**:
```python
async solve()                    # Main entry point
async _plan_solution_steps()     # Generate steps
async _generate_step_content()   # LLM step execution
async _format_final_answer()     # Final formatting
async send_progress()            # Progress callback
```

### 4. Memory System

**Location**: `src/agents/solve/memory/`

**Components**:

#### SolveMemory
Manages the complete solving state:
```python
class SolveMemory:
    task_id: str                          # Unique ID
    user_question: str                    # Original problem
    solve_chains: List[SolveChainStep]   # Steps
    metadata: Dict[str, Any]             # Statistics
```

#### SolveChainStep
Individual solution step:
```python
class SolveChainStep:
    step_id: str                         # e.g., "s001"
    step_target: str                     # Step description
    tool_calls: List[ToolCallRecord]    # Tool usage
    step_response: str                   # Generated content
    status: str                          # State machine
    used_citations: List[str]           # References
```

**Status Flow**:
```
undone → in_progress → waiting_response → done
         └─────────────────── failed ─────┘
```

#### ToolCallRecord
Tracks individual tool invocations:
```python
class ToolCallRecord:
    tool_type: str          # Type of tool
    query: str              # Input query
    raw_answer: str         # Raw output
    summary: str            # Processed summary
    status: str             # Execution state
```

### 5. LLM Service Layer

**Location**: `src/services/llm.py`

**Responsibilities**:
- OpenAI API client configuration
- Async LLM calls with fallback handling
- Response parsing and validation
- Token tracking (optional)

**Key Functions**:
```python
async call_llm(
    user_prompt: str,
    system_prompt: str,
    api_key: str,
    base_url: str,
    model: str,
    temperature: float,
    max_tokens: int,
    response_format: Optional[dict]
) -> str
```

### 6. Configuration System

**Location**: `src/services/config.py` & `config/`

**Configuration Hierarchy**:
1. Default config (hardcoded)
2. YAML config (`config/main.yaml`)
3. Environment variables (`.env`)

**Priority**: Env variables > YAML > Default

**YAML Structure**:
```yaml
system:
  language: "en"
  output_base_dir: "./data/user/solve"

solve:
  max_steps: 5
  max_retries: 2
  agents:
    manager_agent:
      temperature: 0.4
      max_tokens: 4000

llm:
  model: "gpt-4-turbo"
  temperature: 0.7
  max_tokens: 4000
```

## Data Flow

### Request Flow

```
1. User submits problem
   └─> HTTP POST or WebSocket message

2. MainSolver receives request
   └─> Creates output directory
   └─> Initializes SolveMemory

3. Planning Phase
   └─> LLM generates steps
   └─> SolveMemory.create_chains()

4. Solving Phase (per step)
   └─> LLM generates content
   └─> SolveChainStep.update_response()
   └─> Progress callback triggered
   └─> send_progress() to WebSocket

5. Formatting Phase
   └─> LLM creates final answer
   └─> Save to markdown/JSON

6. Return Results
   └─> Send result message
   └─> Send complete signal
```

### Memory Persistence

**Output Directory Structure**:
```
./data/user/solve/solve_20240114_120000/
├── solve_chain.json      # Complete state
├── final_answer.md       # Formatted solution
├── result.json          # Result summary
└── artifacts/           # Generated files
```

**Save Points**:
1. After creating steps (Planning)
2. After each step execution (Solving)
3. After formatting (Final)

## Scalability Considerations

### Current Architecture
- Single instance, async processing
- Suitable for: 10-50 concurrent users
- Request queue handled by OS

### Horizontal Scaling
To scale to 1000+ users:

1. **Load Balancing**
   - Use Nginx/HAProxy
   - Distribute across multiple server instances

2. **Async Task Queue**
   - Celery + Redis for job distribution
   - Process long-running solves asynchronously

3. **Database Layer**
   - MongoDB for flexible document storage
   - Redis for caching and session state

4. **Monitoring**
   - Prometheus for metrics
   - ELK stack for logs
   - Sentry for error tracking

**Proposed High-Scale Architecture**:
```
        ┌─────────────┐
        │   Load      │
        │  Balancer   │
        │  (Nginx)    │
        └─────┬───────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
  ┌───┐   ┌───┐   ┌───┐
  │API│   │API│   │API│
  │ 1 │   │ 2 │   │ 3 │
  └─┬─┘   └─┬─┘   └─┬─┘
    │       │       │
    └───────┼───────┘
            │
        ┌───▼───────────┐
        │ Celery Queue  │
        │ (Redis)       │
        └───┬───────────┘
            │
    ┌───────┼───────────┐
    │       │           │
    ▼       ▼           ▼
  ┌─────┐ ┌─────┐ ┌─────┐
  │Wrk 1│ │Wrk 2│ │Wrk N│
  └──┬──┘ └──┬──┘ └──┬──┘
     │       │       │
     └───────┼───────┘
             │
        ┌────▼──────┐
        │ MongoDB   │
        │ (Results) │
        └───────────┘
```

## Error Handling

### Error Levels

1. **Validation Errors** (400)
   - Missing required fields
   - Invalid input format

2. **LLM Errors** (503)
   - API key invalid
   - Rate limit exceeded
   - Model unavailable

3. **System Errors** (500)
   - Disk space full
   - Memory exhausted
   - File permission issues

### Retry Strategy

```python
for attempt in range(max_retries):
    try:
        result = await call_llm(...)
        break
    except RateLimitError:
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
    except Exception as e:
        if attempt == max_retries - 1:
            raise
```

## Extension Points

### Adding New Agent Types

1. Create agent class inheriting from `BaseAgent`
2. Implement `async process()` method
3. Register in `MainSolver._init_agents()`
4. Add YAML configuration
5. Integrate into workflow

### Adding New Tools

1. Create tool function in `src/tools/`
2. Register in `ToolAgent`
3. Add tool execution logic
4. Update tool schema documentation

### Adding New Problem Types

1. Create specialized solver inheriting `MainSolver`
2. Override `_plan_solution_steps()`
3. Customize prompts for domain
4. Register in API routers

## Performance Metrics

### Typical Response Times

| Phase | Time | Notes |
|-------|------|-------|
| Planning | 3-5s | LLM inference |
| Per Step | 5-10s | Depends on complexity |
| Formatting | 2-3s | Final answer generation |
| **Total** | **20-50s** | For 4-5 steps |

### Resource Usage

| Resource | Typical | Peak |
|----------|---------|------|
| Memory | 200-500MB | 1-2GB |
| CPU | 20-40% | 80-100% |
| Network | 1-2MB | 5-10MB |
| Disk I/O | Low | During save |

## Security Considerations

### API Security
- [ ] Implement API key authentication
- [ ] Rate limiting per API key
- [ ] HTTPS/TLS for production
- [ ] CORS whitelist for domains

### Data Security
- [ ] Encrypt stored solutions
- [ ] Secure API key management
- [ ] Input sanitization
- [ ] OWASP compliance

### LLM Security
- [ ] Prompt injection protection
- [ ] Output validation
- [ ] Token limit enforcement
- [ ] Audit logging

## Deployment Strategies

### Development
- Single instance
- Hot reload enabled
- Debug mode on
- File-based persistence

### Production (Docker)
- Multi-container setup
- Health checks enabled
- Log aggregation
- Persistent volumes

### Cloud (Kubernetes)
- Containerized
- Auto-scaling policies
- Service mesh integration
- Distributed logging

## Monitoring & Observability

### Metrics to Track
- Request latency percentiles
- Error rate by type
- LLM token usage
- Memory consumption
- Cache hit ratios

### Logging Strategy
- Request/response logging
- Error stack traces
- Performance metrics
- Audit trails

### Alerting Rules
- Error rate > 5%
- Response latency > 60s
- Memory usage > 80%
- Disk space < 10%

---

**Architecture Version**: 1.0.0  
**Last Updated**: January 2024  
**Status**: Production Ready
