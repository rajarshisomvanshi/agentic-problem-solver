# Configuration & Customization Guide

Complete guide to configuring and customizing Agentic Problem Solver.

## Quick Reference

### Environment Variables (.env)

```bash
# Critical (required)
GEMINI_API_KEY=AIzaSy...              # Gemini API key

# API Server
OPENAI_BASE_URL=https://api.openai.com/v1   # LLM endpoint
LLM_MODEL=gpt-4-turbo                        # Model to use
API_HOST=0.0.0.0                             # Server host
API_PORT=8000                                # Server port

# Environment
ENVIRONMENT=development                      # development|production
DEBUG=true                                   # Enable debug mode

# Logging
LOG_LEVEL=INFO                               # DEBUG|INFO|WARNING|ERROR
LOG_DIR=./data/user/logs                     # Log directory

# Problem Solving
MAX_SOLVE_STEPS=5                            # Max solution steps
SOLVE_TIMEOUT=300                            # Timeout in seconds
SAVE_INTERMEDIATE_RESULTS=true               # Save during solving

# LLM Parameters
LLM_TEMPERATURE=0.7                          # 0.0-1.0 (randomness)
LLM_MAX_TOKENS=4000                          # Max response length
```

## YAML Configuration (config/main.yaml)

### System Settings

```yaml
system:
  language: "en"                     # Language for output
  output_base_dir: "./data/user/solve"  # Output directory
  max_output_tokens: 10000           # Max total output
```

**Available Languages**: en, zh (extensible)

### Solver Configuration

```yaml
solve:
  max_steps: 5                       # Maximum solution steps (3-10)
  max_retries: 2                     # Retry failed steps
  timeout: 300                       # Total timeout (seconds)
  save_intermediate_results: true    # Save after each step
  
  agents:
    manager_agent:
      temperature: 0.4               # Lower = more consistent
      max_tokens: 4000               # Tokens for planning
      
    solve_agent:
      temperature: 0.7               # Higher = more creative
      max_tokens: 8192               # Tokens per step
      
    response_agent:
      temperature: 0.5               # Balanced
      max_tokens: 4096               # Tokens for formatting
```

### LLM Settings

```yaml
llm:
  model: "gpt-4-turbo"              # Model choice
  temperature: 0.7                   # Overall temperature
  max_tokens: 4000                   # Default token limit
  timeout: 120                       # LLM request timeout (sec)
  top_p: 0.9                        # Nucleus sampling
  frequency_penalty: 0               # Repeat penalty
  presence_penalty: 0                # New token penalty
```

**Temperature Guidelines**:
- 0.0-0.3: Deterministic, consistent (planning)
- 0.4-0.6: Balanced (general)
- 0.7-1.0: Creative, varied (brainstorming)

### Logging Configuration

```yaml
logging:
  level: "INFO"                      # DEBUG|INFO|WARNING|ERROR|CRITICAL
  log_dir: "./data/user/logs"        # Log file directory
  console_output: true               # Print to console
  save_to_file: true                 # Write to file
  format: "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
```

**Log Levels**:
- `DEBUG`: Verbose internal operations
- `INFO`: General progress messages
- `WARNING`: Potential issues
- `ERROR`: Failures
- `CRITICAL`: System failures

### API Configuration

```yaml
api:
  host: "0.0.0.0"                   # Listening address
  port: 8000                        # Listening port
  reload: true                      # Auto-reload on changes
  log_level: "info"                # Uvicorn log level
```

### Path Configuration

```yaml
paths:
  solve_output_dir: "./data/user/solve"   # Results storage
  user_log_dir: "./data/user/logs"        # Log files
  config_dir: "./config"                  # Config files
```

## Customization Examples

### Example 1: Fast, Deterministic Solving

**Use Case**: Consistent, predictable solutions

```yaml
# config/main.yaml
solve:
  max_steps: 3
  timeout: 120
  agents:
    manager_agent:
      temperature: 0.2
      max_tokens: 2000
    solve_agent:
      temperature: 0.3
      max_tokens: 4000

llm:
  model: "gpt-4-turbo"
  temperature: 0.3
  max_tokens: 2000
  timeout: 60
```

**.env**:
```bash
LLM_MAX_TOKENS=2000
SOLVE_TIMEOUT=120
MAX_SOLVE_STEPS=3
```

### Example 2: Detailed, Creative Solutions

**Use Case**: Comprehensive, exploratory answers

```yaml
# config/main.yaml
solve:
  max_steps: 7
  timeout: 600
  agents:
    manager_agent:
      temperature: 0.6
      max_tokens: 8000
    solve_agent:
      temperature: 0.8
      max_tokens: 16000

llm:
  model: "gpt-4-turbo"
  temperature: 0.8
  max_tokens: 8000
  timeout: 180
```

**.env**:
```bash
LLM_MAX_TOKENS=8000
SOLVE_TIMEOUT=600
MAX_SOLVE_STEPS=7
LLM_TEMPERATURE=0.8
```

### Example 3: Production (Cost-Optimized)

**Use Case**: Minimize API costs

```yaml
# config/main.yaml
solve:
  max_steps: 4
  timeout: 180
  agents:
    manager_agent:
      temperature: 0.4
      max_tokens: 1500
    solve_agent:
      temperature: 0.5
      max_tokens: 2000

llm:
  model: "gpt-4-turbo"
  temperature: 0.5
  max_tokens: 1500
  timeout: 90
```

**.env**:
```bash
LLM_MAX_TOKENS=1500
SOLVE_TIMEOUT=180
MAX_SOLVE_STEPS=4
LLM_TEMPERATURE=0.5
ENVIRONMENT=production
DEBUG=false
```

### Example 4: Multi-Language Support

**Use Case**: Support multiple languages

```yaml
# config/main.yaml
system:
  language: "zh"  # Chinese output

# config/prompts_zh/main_solver.yaml
# (Create Chinese prompts)
```

**.env**:
```bash
# Additional language-specific settings
```

## Advanced Configuration

### Using Alternative LLM Providers

#### Ollama (Local LLM)

```bash
# .env
GEMINI_API_KEY=not-needed
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama2:13b
```

#### Azure OpenAI

```bash
# .env
GEMINI_API_KEY=your-gemini-key
OPENAI_BASE_URL=https://your-resource.openai.azure.com/v1
LLM_MODEL=gpt-4
```

#### Anthropic Claude

```bash
# Requires code modification in llm.py
# Use anthropic library instead of openai
```

### Custom Prompts

To customize prompts:

1. Create `config/prompts/` directory
2. Add `manager_prompt.txt`, `solver_prompt.txt`, etc.
3. Modify `main_solver.py` to load custom prompts

```python
# In main_solver.py
def _load_system_prompt(self, agent_type):
    prompt_file = f"config/prompts/{agent_type}_prompt.txt"
    with open(prompt_file) as f:
        return f.read()
```

### Custom Output Format

Extend `_format_final_answer()`:

```python
# In main_solver.py
async def _format_final_answer(self, question, steps):
    # Custom formatting logic
    result = {
        "question": question,
        "steps": [s.to_dict() for s in steps],
        "custom_field": "value"
    }
    return json.dumps(result, indent=2)
```

## Performance Tuning

### Optimize for Speed

```yaml
solve:
  max_steps: 2
  timeout: 60
  agents:
    manager_agent:
      temperature: 0.2
      max_tokens: 1000
    solve_agent:
      temperature: 0.3
      max_tokens: 2000

llm:
  temperature: 0.2
  max_tokens: 1000
  timeout: 30
```

### Optimize for Quality

```yaml
solve:
  max_steps: 10
  timeout: 900
  agents:
    manager_agent:
      temperature: 0.5
      max_tokens: 8000
    solve_agent:
      temperature: 0.7
      max_tokens: 16000

llm:
  temperature: 0.7
  max_tokens: 8000
  timeout: 300
```

### Optimize for Cost

```yaml
solve:
  max_steps: 3
  timeout: 120
  
llm:
  max_tokens: 1000
  timeout: 60
  frequency_penalty: 0.5  # Reduce repetition
```

## Monitoring Configuration

### Enable Detailed Logging

```bash
# .env
LOG_LEVEL=DEBUG
DEBUG=true
```

### Disable in Production

```bash
# .env
LOG_LEVEL=ERROR
DEBUG=false
ENVIRONMENT=production
```

## Directory Structure Configuration

### Change Output Location

```bash
# .env
OUTPUT_DIR=/mnt/storage/solver_outputs
LOG_DIR=/var/log/solver
```

### Or in YAML

```yaml
paths:
  solve_output_dir: /mnt/storage/solver_outputs
  user_log_dir: /var/log/solver
```

## Configuration Validation

### Verify Configuration

```bash
python -c "
from src.services.config import load_config
config = load_config()
print(config)
"
```

### Validate Environment

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required = ['GEMINI_API_KEY', 'LLM_MODEL']
for key in required:
    if not os.getenv(key):
        print(f'Missing: {key}')
    else:
        print(f'✓ {key}')
"
```

## Troubleshooting Configuration

### Problem: "Configuration not loading"

**Solution**:
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config/main.yaml'))"

# Check .env file
cat .env

# Verify environment loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
```

### Problem: "Wrong LLM settings being used"

**Solution**:
Priority order (highest to lowest):
1. Environment variables (.env)
2. YAML config
3. Code defaults

Check what's being loaded:
```python
from src.services.config import load_config
from src.services.llm import get_llm_config

config = load_config()
print("Config:", config)

llm_config = get_llm_config()
print("LLM Config:", llm_config)
```

## Best Practices

1. **Version Control**
   - Commit `config/main.yaml`
   - Never commit `.env` (add to .gitignore)
   - Use `.env.example` as template

2. **Environment-Specific Configs**
   - `config/main.yaml` - Common settings
   - `.env.development` - Dev overrides
   - `.env.production` - Prod overrides

3. **Sensitive Data**
   - Never commit API keys
   - Use secret management (AWS Secrets, Vault)
   - Rotate keys regularly

4. **Documentation**
   - Document custom configurations
   - Keep configuration changelog
   - Update SETUP.md with changes

---

**Configuration Version**: 1.0.0  
**Last Updated**: January 2024
