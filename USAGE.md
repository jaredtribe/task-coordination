# Usage Guide

## Installation

### Option 1: Install with pip
```bash
cd cli/
pip install -e .
```

### Option 2: Run directly (no installation)
```bash
# Set up environment
export TASK_API_URL="http://jean-host:8080"
export AGENT_ID="jared"

# Run CLI
python3 -m tqc.main add "Test task" --kind email --priority 20
```

## Configuration

The CLI reads configuration from environment variables:

```bash
export TASK_API_URL="http://api-host:8080"  # Required
export AGENT_ID="jared"                     # Optional, can use --agent flag
export REDIS_URL="redis://localhost:6379/0" # Optional, for future pub/sub
```

## Examples

### Add a task
```bash
tqc add "Triage urgent email from Sarah" \
  --kind email \
  --priority 20 \
  --tier standard \
  --desc "Check inbox, draft reply if needed"
```

### List tasks
```bash
# All tasks
tqc list

# Filter by status
tqc list --status queued

# Filter by agent
tqc list --agent jared --status running

# Filter by kind
tqc list --kind email
```

### Get task details
```bash
tqc get 42
```

### Claim a task
```bash
# Claim task #42
tqc claim 42
```

### Update task status
```bash
# Mark as running
tqc update 42 --status running

# Mark as failed
tqc update 42 --status failed
```

### Complete a task
```bash
# Simple completion
tqc complete 42 --result "Email draft saved"

# With artifacts
tqc complete 42 \
  --result "Email draft saved to drafts/" \
  --artifacts '["drafts/email-42.md"]'
```

### Cancel a task
```bash
tqc cancel 42
```

### Agent heartbeat
```bash
# Register heartbeat
tqc heartbeat

# With capabilities
tqc heartbeat --capabilities '{"email":true,"github":true,"browser":true}'
```

### List agents
```bash
tqc agents
```

---

## Integration with Clawdbot Agents

### Jared's Heartbeat Pattern

Update `HEARTBEAT.md`:
```markdown
### Email Check
- [ ] Scan inbox for urgent items
- [ ] If urgent email found:
  ```bash
  tqc add "Triage urgent email from $SENDER" \
    --kind email \
    --priority 20 \
    --tier standard
  ```
```

### Worker Pattern

Spawn a worker agent to process tasks:

```bash
# In a cron job or background loop
while true; do
  # Find next queued task
  TASK_ID=$(tqc list --status queued --limit 1 | grep -oP '^\#\K\d+')
  
  if [ -n "$TASK_ID" ]; then
    # Claim it
    tqc claim $TASK_ID
    
    # Execute (spawn sub-agent)
    clawdbot sessions spawn \
      --task "Execute task #$TASK_ID from queue" \
      --label "worker-task-$TASK_ID"
    
    # Worker completes and calls: tqc complete $TASK_ID --result "..."
  fi
  
  sleep 30
done
```

---

## Testing (Once API is Ready)

```bash
# Set up
export TASK_API_URL="http://jean-api-host:8080"
export AGENT_ID="jared"

# Test add
tqc add "Test task" --kind general --priority 50

# Test list
tqc list

# Test claim
tqc claim 1

# Test status update
tqc update 1 --status running

# Test complete
tqc complete 1 --result "Done!"

# Test heartbeat
tqc heartbeat
```

---

## Troubleshooting

### "Error: Failed to initialize client"
- Check TASK_API_URL is set correctly
- Verify API is running and accessible
- Test: `curl $TASK_API_URL/tasks`

### "HTTP 409 Conflict" when claiming
- Task is already claimed by another agent
- List tasks to see current status: `tqc list`

### "HTTP 404 Not Found"
- Task ID doesn't exist
- Check task list: `tqc list`
