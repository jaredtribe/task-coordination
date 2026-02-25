# Task Coordination API Reference

REST API specification for Jean to implement.

## Base URL
`http://<host>:8080` (configure port as needed)

## Authentication
Optional: Include `X-Agent-ID` header with agent identifier.

## Endpoints

### Tasks

#### POST /tasks
Create a new task.

**Request:**
```json
{
  "title": "Task title",
  "description": "Optional description",
  "kind": "email",
  "priority": 20,
  "model_tier": "standard",
  "metadata": {}
}
```

**Response:** `201 Created`
```json
{
  "id": 42,
  "title": "Task title",
  "description": "Optional description",
  "kind": "email",
  "priority": 20,
  "model_tier": "standard",
  "status": "queued",
  "claimed_by": null,
  "claimed_at": null,
  "created_at": "2024-02-25T18:00:00Z",
  "updated_at": "2024-02-25T18:00:00Z",
  "completed_at": null,
  "result": null,
  "metadata": {}
}
```

#### GET /tasks
List tasks with optional filters.

**Query Parameters:**
- `status` - Filter by status (queued, claimed, running, done, failed)
- `agent` - Filter by agent ID
- `kind` - Filter by task kind
- `limit` - Max results (default: 20)
- `offset` - Pagination offset (default: 0)

**Response:** `200 OK`
```json
[
  {
    "id": 42,
    "title": "Task title",
    "kind": "email",
    "status": "queued",
    "priority": 20,
    ...
  }
]
```

#### GET /tasks/:id
Get task details.

**Response:** `200 OK`
```json
{
  "id": 42,
  "title": "Task title",
  ...
}
```

**Error:** `404 Not Found` if task doesn't exist

#### POST /tasks/:id/claim
Claim a task for execution.

**Request:** (optional body with agent ID if not in header)
```json
{
  "agent_id": "jared"
}
```

**Response:** `200 OK`
```json
{
  "id": 42,
  "status": "claimed",
  "claimed_by": "jared",
  "claimed_at": "2024-02-25T18:01:00Z",
  ...
}
```

**Error:** 
- `404 Not Found` - Task doesn't exist
- `409 Conflict` - Task already claimed by another agent

#### PATCH /tasks/:id/status
Update task status.

**Request:**
```json
{
  "status": "running"
}
```

**Response:** `200 OK`
```json
{
  "id": 42,
  "status": "running",
  ...
}
```

**Error:**
- `404 Not Found` - Task doesn't exist
- `400 Bad Request` - Invalid status

#### POST /tasks/:id/complete
Mark task as complete.

**Request:**
```json
{
  "result": {
    "description": "Email draft saved to drafts/",
    "artifacts": ["drafts/email-42.md"]
  }
}
```

**Response:** `200 OK`
```json
{
  "id": 42,
  "status": "done",
  "completed_at": "2024-02-25T18:05:00Z",
  "result": { ... },
  ...
}
```

**Error:** `404 Not Found` - Task doesn't exist

#### DELETE /tasks/:id
Cancel a task.

**Response:** `204 No Content`

**Error:** `404 Not Found` - Task doesn't exist

---

### Agents

#### GET /agents
List registered agents.

**Response:** `200 OK`
```json
[
  {
    "id": "jared",
    "host": "ip-172-31-43-104",
    "last_heartbeat": "2024-02-25T18:10:00Z",
    "capabilities": {
      "email": true,
      "github": true,
      "browser": true
    }
  }
]
```

#### POST /agents/heartbeat
Register agent heartbeat.

**Request:**
```json
{
  "agent_id": "jared",
  "host": "ip-172-31-43-104",
  "capabilities": {
    "email": true,
    "github": true,
    "browser": true
  }
}
```

**Response:** `200 OK`
```json
{
  "id": "jared",
  "host": "ip-172-31-43-104",
  "last_heartbeat": "2024-02-25T18:10:00Z",
  "capabilities": { ... }
}
```

---

## Error Responses

All errors return appropriate HTTP status codes with JSON body:

```json
{
  "error": "Error message",
  "details": "Optional additional details"
}
```

Common status codes:
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource conflict (e.g., task already claimed)
- `500 Internal Server Error` - Server error

---

## Implementation Notes

### Task Claiming Logic
- When claiming a task, check if `claimed_by` is NULL
- Use database transaction to prevent race conditions
- Set `claimed_at` timestamp
- Update status to `claimed`

### Heartbeat Cleanup
Consider a background job to mark agents inactive if last_heartbeat is stale (e.g., >5 minutes).

### Status Transitions
Valid transitions:
- `queued` → `claimed` → `running` → `done` or `failed`
- Any status → `queued` (reset/retry)

### CORS
If needed for browser access, enable CORS headers.
