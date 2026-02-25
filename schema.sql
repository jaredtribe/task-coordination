-- Task Coordination Service Schema
-- For Jean to implement in the Postgres backend

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    kind TEXT NOT NULL DEFAULT 'general', -- code, email, research, browser, review, verify
    priority INTEGER NOT NULL DEFAULT 50, -- 0=critical, 50=normal, 100=low
    model_tier TEXT NOT NULL DEFAULT 'standard', -- light, standard, heavy
    status TEXT NOT NULL DEFAULT 'queued', -- queued, claimed, running, done, failed
    claimed_by TEXT, -- agent ID that claimed this task
    claimed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    result JSONB, -- execution result, output, artifacts
    metadata JSONB -- flexible extension data
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_claimed_by ON tasks(claimed_by);
CREATE INDEX IF NOT EXISTS idx_tasks_kind ON tasks(kind);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY, -- agent identifier (jared, jean, etc)
    host TEXT, -- hostname/IP
    last_heartbeat TIMESTAMP NOT NULL DEFAULT NOW(),
    capabilities JSONB, -- what this agent can do
    metadata JSONB -- additional agent info
);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Comments for documentation
COMMENT ON TABLE tasks IS 'Task queue for agent coordination';
COMMENT ON TABLE agents IS 'Registered agents in the system';

COMMENT ON COLUMN tasks.kind IS 'Task type: general, code, email, research, browser, review, verify';
COMMENT ON COLUMN tasks.priority IS 'Priority: 0=critical, 50=normal, 100=low';
COMMENT ON COLUMN tasks.model_tier IS 'Model tier: light (Haiku/Sonnet3.5), standard (Sonnet4.5), heavy (Opus4.5)';
COMMENT ON COLUMN tasks.status IS 'Status: queued, claimed, running, done, failed';
