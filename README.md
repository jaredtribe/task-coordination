# Task Coordination Service

Shared task queue and coordination infrastructure for multi-agent Clawdbot deployments.

## Architecture

- **Postgres** - Persistent task storage, agent registry
- **Redis** - Fast task claiming, pub/sub notifications
- **REST API** - HTTP interface (built by Jean)
- **CLI Client** (`tqc`) - Command-line interface for agents

## Components

### 1. Database (Postgres)
Schema for tasks, agents, and execution tracking.

### 2. Redis Layer
- Task claim locking (prevent double-execution)
- Pub/sub for task notifications
- Agent heartbeat tracking

### 3. Client CLI (`tqc`)
Python CLI that both Jared and Jean use to interact with the coordination service.

```bash
# Add a task
tqc add "Triage urgent email from Sarah" --kind email --priority 20 --tier standard

# List tasks
tqc list --status queued
tqc list --agent jared --status running

# Claim a task
tqc claim 42

# Update task status
tqc update 42 --status running

# Complete task
tqc complete 42 --result "Email draft saved to drafts/"

# Agent heartbeat
tqc heartbeat --agent jared
```

## Setup

### Dependencies
- Docker & Docker Compose (for Redis)
- Python 3.9+
- Postgres (provided by Jean's API instance)

### Installation

```bash
# Install CLI
cd cli/
pip install -e .

# Configure endpoint
export TASK_API_URL="http://jean-host:8080"
export AGENT_ID="jared"  # or "jean"

# Start Redis (optional, for local dev)
docker-compose up -d redis
```

## Task Queue Model

### Task States
- `queued` - Ready to be claimed
- `claimed` - Agent has claimed it
- `running` - Agent is executing
- `done` - Completed successfully
- `failed` - Execution failed

### Task Priority
- `0-20` - Critical (urgent emails, CI failures)
- `21-50` - Normal (standard operations)
- `51-100` - Low (background work, cleanup)

### Model Tiers
- `light` - Fast, cheap models (Haiku/Sonnet 3.5) for triage, status checks
- `standard` - Capable models (Sonnet 4.5) for email drafts, code review
- `heavy` - Powerful models (Opus 4.5) for architecture, complex reasoning

## Development

### Current Status
- [x] Repo structure
- [ ] Redis container setup
- [ ] Python CLI client (`tqc`)
- [ ] API client library
- [ ] Integration with Jean's REST API
- [ ] Agent heartbeat mechanism
- [ ] Pub/sub notification system

### Building
**Jared**: Redis layer + CLI client
**Jean**: Postgres schema + REST API

## API Endpoints (Jean's Implementation)

```
POST   /tasks              - Add task
GET    /tasks              - List tasks (filter by status, agent, kind)
GET    /tasks/:id          - Get task details
POST   /tasks/:id/claim    - Claim task for execution
PATCH  /tasks/:id/status   - Update task status
POST   /tasks/:id/complete - Mark done + result
DELETE /tasks/:id          - Cancel task

GET    /agents             - Agent registry
POST   /agents/heartbeat   - Agent check-in
```

## License
MIT
