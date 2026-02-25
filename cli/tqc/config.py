"""Configuration management for task queue client."""

import os
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    return {
        'api_url': os.getenv('TASK_API_URL', ''),
        'agent_id': os.getenv('AGENT_ID', ''),
        'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    }
