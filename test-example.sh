#!/bin/bash
# Example test script for task coordination CLI
# Run this once Jean's API is up

set -e

echo "=== Task Coordination CLI Test ==="
echo ""

# Check config
echo "Configuration:"
tqc config
echo ""

# Add some test tasks
echo "Adding test tasks..."
tqc add "Test email task" --kind email --priority 20 --tier standard
tqc add "Test code task" --kind code --priority 30 --tier heavy
tqc add "Test research task" --kind research --priority 50 --tier light
echo ""

# List all tasks
echo "All tasks:"
tqc list
echo ""

# Filter by status
echo "Queued tasks:"
tqc list --status queued
echo ""

# Claim first task
echo "Claiming task #1..."
tqc claim 1
echo ""

# Update status
echo "Updating task #1 to running..."
tqc update 1 --status running
echo ""

# List running tasks
echo "Running tasks:"
tqc list --status running
echo ""

# Complete task
echo "Completing task #1..."
tqc complete 1 --result "Test completed successfully"
echo ""

# Register heartbeat
echo "Registering heartbeat..."
tqc heartbeat --capabilities '{"email":true,"code":true,"research":true}'
echo ""

# List agents
echo "Registered agents:"
tqc agents
echo ""

echo "=== Test Complete ==="
