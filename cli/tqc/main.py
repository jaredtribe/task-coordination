#!/usr/bin/env python3
"""Task Queue Client - Main CLI entry point."""

import sys
import os
import argparse
import json
from typing import Optional, Dict, Any

from .client import TaskClient
from .config import load_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Task Queue Client - shared task coordination for agents"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add task
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('--desc', '--description', help='Task description')
    add_parser.add_argument('--kind', default='general', 
                           choices=['general', 'code', 'email', 'research', 'browser', 'review', 'verify'],
                           help='Task type')
    add_parser.add_argument('--priority', type=int, default=50, 
                           help='Priority (0=critical, 50=normal, 100=low)')
    add_parser.add_argument('--tier', default='standard',
                           choices=['light', 'standard', 'heavy'],
                           help='Model tier')
    add_parser.add_argument('--metadata', help='Additional metadata (JSON string)')
    
    # List tasks
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--agent', help='Filter by agent')
    list_parser.add_argument('--kind', help='Filter by kind')
    list_parser.add_argument('--limit', type=int, default=20, help='Max results')
    
    # Get task
    get_parser = subparsers.add_parser('get', help='Get task details')
    get_parser.add_argument('task_id', type=int, help='Task ID')
    
    # Claim task
    claim_parser = subparsers.add_parser('claim', help='Claim a task')
    claim_parser.add_argument('task_id', type=int, help='Task ID')
    
    # Update task
    update_parser = subparsers.add_parser('update', help='Update task status')
    update_parser.add_argument('task_id', type=int, help='Task ID')
    update_parser.add_argument('--status', required=True,
                               choices=['queued', 'claimed', 'running', 'done', 'failed'])
    
    # Complete task
    complete_parser = subparsers.add_parser('complete', help='Mark task as complete')
    complete_parser.add_argument('task_id', type=int, help='Task ID')
    complete_parser.add_argument('--result', help='Result description or output')
    complete_parser.add_argument('--artifacts', help='Artifacts (JSON string)')
    
    # Cancel task
    cancel_parser = subparsers.add_parser('cancel', help='Cancel a task')
    cancel_parser.add_argument('task_id', type=int, help='Task ID')
    
    # Agent heartbeat
    heartbeat_parser = subparsers.add_parser('heartbeat', help='Register agent heartbeat')
    heartbeat_parser.add_argument('--agent', help='Agent ID (defaults to config)')
    heartbeat_parser.add_argument('--capabilities', help='Agent capabilities (JSON)')
    
    # Agent list
    agents_parser = subparsers.add_parser('agents', help='List registered agents')
    
    # Config
    config_parser = subparsers.add_parser('config', help='Show current configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle config command (no client needed)
    if args.command == 'config':
        config = load_config()
        print(json.dumps(config, indent=2))
        return
    
    # Initialize client
    try:
        client = TaskClient()
    except Exception as e:
        print(f"Error: Failed to initialize client: {e}", file=sys.stderr)
        print("\nMake sure TASK_API_URL is set:", file=sys.stderr)
        print("  export TASK_API_URL=http://api-host:8080", file=sys.stderr)
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'add':
            metadata = json.loads(args.metadata) if args.metadata else None
            result = client.add_task(
                title=args.title,
                description=args.desc,
                kind=args.kind,
                priority=args.priority,
                model_tier=args.tier,
                metadata=metadata
            )
            print(f"Task added: #{result['id']}")
            print(json.dumps(result, indent=2))
        
        elif args.command == 'list':
            filters = {}
            if args.status:
                filters['status'] = args.status
            if args.agent:
                filters['agent'] = args.agent
            if args.kind:
                filters['kind'] = args.kind
            filters['limit'] = args.limit
            
            tasks = client.list_tasks(**filters)
            if not tasks:
                print("No tasks found.")
            else:
                print(f"Found {len(tasks)} task(s):\n")
                for task in tasks:
                    print(f"#{task['id']} [{task['status']}] {task['title']}")
                    print(f"  Kind: {task['kind']} | Priority: {task['priority']} | Tier: {task['model_tier']}")
                    if task.get('claimed_by'):
                        print(f"  Claimed by: {task['claimed_by']}")
                    print()
        
        elif args.command == 'get':
            task = client.get_task(args.task_id)
            print(json.dumps(task, indent=2))
        
        elif args.command == 'claim':
            result = client.claim_task(args.task_id)
            print(f"Task #{args.task_id} claimed successfully")
            print(json.dumps(result, indent=2))
        
        elif args.command == 'update':
            result = client.update_status(args.task_id, args.status)
            print(f"Task #{args.task_id} status updated to: {args.status}")
        
        elif args.command == 'complete':
            result_data = None
            if args.result or args.artifacts:
                result_data = {}
                if args.result:
                    result_data['description'] = args.result
                if args.artifacts:
                    result_data['artifacts'] = json.loads(args.artifacts)
            
            result = client.complete_task(args.task_id, result_data)
            print(f"Task #{args.task_id} completed")
        
        elif args.command == 'cancel':
            result = client.cancel_task(args.task_id)
            print(f"Task #{args.task_id} cancelled")
        
        elif args.command == 'heartbeat':
            agent_id = args.agent or client.config.get('agent_id')
            if not agent_id:
                print("Error: No agent ID specified. Use --agent or set AGENT_ID", file=sys.stderr)
                sys.exit(1)
            
            capabilities = json.loads(args.capabilities) if args.capabilities else None
            result = client.heartbeat(agent_id, capabilities)
            print(f"Heartbeat registered for {agent_id}")
        
        elif args.command == 'agents':
            agents = client.list_agents()
            if not agents:
                print("No agents registered.")
            else:
                print(f"Registered agents ({len(agents)}):\n")
                for agent in agents:
                    print(f"{agent['id']}")
                    print(f"  Host: {agent.get('host', 'unknown')}")
                    if agent.get('last_heartbeat'):
                        print(f"  Last heartbeat: {agent['last_heartbeat']}")
                    print()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
