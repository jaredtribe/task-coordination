"""API client for task coordination service."""

import os
import requests
from typing import Optional, Dict, Any, List

from .config import load_config


class TaskClient:
    """Client for interacting with the task coordination API."""
    
    def __init__(self, api_url: Optional[str] = None, agent_id: Optional[str] = None):
        """Initialize client.
        
        Args:
            api_url: API base URL (defaults to config/env)
            agent_id: Agent identifier (defaults to config/env)
        """
        self.config = load_config()
        self.api_url = api_url or self.config.get('api_url')
        self.agent_id = agent_id or self.config.get('agent_id')
        
        if not self.api_url:
            raise ValueError("API URL not configured. Set TASK_API_URL environment variable.")
        
        # Remove trailing slash
        self.api_url = self.api_url.rstrip('/')
        
        self.session = requests.Session()
        if self.agent_id:
            self.session.headers.update({'X-Agent-ID': self.agent_id})
    
    def _request(self, method: str, path: str, **kwargs) -> Any:
        """Make API request.
        
        Args:
            method: HTTP method
            path: API path
            **kwargs: Additional request arguments
        
        Returns:
            Response JSON data
        
        Raises:
            requests.HTTPError: On HTTP error
        """
        url = f"{self.api_url}{path}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        
        if response.status_code == 204:  # No content
            return None
        
        return response.json()
    
    def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        kind: str = 'general',
        priority: int = 50,
        model_tier: str = 'standard',
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a new task.
        
        Args:
            title: Task title
            description: Task description
            kind: Task type
            priority: Priority (0=critical, 50=normal, 100=low)
            model_tier: Model tier (light, standard, heavy)
            metadata: Additional metadata
        
        Returns:
            Created task data
        """
        payload = {
            'title': title,
            'kind': kind,
            'priority': priority,
            'model_tier': model_tier
        }
        
        if description:
            payload['description'] = description
        if metadata:
            payload['metadata'] = metadata
        
        return self._request('POST', '/tasks', json=payload)
    
    def list_tasks(
        self,
        status: Optional[str] = None,
        agent: Optional[str] = None,
        kind: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filters.
        
        Args:
            status: Filter by status
            agent: Filter by agent
            kind: Filter by kind
            limit: Max results
        
        Returns:
            List of tasks
        """
        params = {'limit': limit}
        if status:
            params['status'] = status
        if agent:
            params['agent'] = agent
        if kind:
            params['kind'] = kind
        
        return self._request('GET', '/tasks', params=params)
    
    def get_task(self, task_id: int) -> Dict[str, Any]:
        """Get task details.
        
        Args:
            task_id: Task ID
        
        Returns:
            Task data
        """
        return self._request('GET', f'/tasks/{task_id}')
    
    def claim_task(self, task_id: int) -> Dict[str, Any]:
        """Claim a task for execution.
        
        Args:
            task_id: Task ID
        
        Returns:
            Updated task data
        """
        return self._request('POST', f'/tasks/{task_id}/claim')
    
    def update_status(self, task_id: int, status: str) -> Dict[str, Any]:
        """Update task status.
        
        Args:
            task_id: Task ID
            status: New status
        
        Returns:
            Updated task data
        """
        return self._request('PATCH', f'/tasks/{task_id}/status', json={'status': status})
    
    def complete_task(
        self,
        task_id: int,
        result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Mark task as complete.
        
        Args:
            task_id: Task ID
            result: Result data (description, artifacts, etc)
        
        Returns:
            Updated task data
        """
        payload = {}
        if result:
            payload['result'] = result
        
        return self._request('POST', f'/tasks/{task_id}/complete', json=payload)
    
    def cancel_task(self, task_id: int) -> None:
        """Cancel a task.
        
        Args:
            task_id: Task ID
        """
        self._request('DELETE', f'/tasks/{task_id}')
    
    def heartbeat(
        self,
        agent_id: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register agent heartbeat.
        
        Args:
            agent_id: Agent identifier (defaults to client's agent_id)
            capabilities: Agent capabilities
        
        Returns:
            Agent data
        """
        agent = agent_id or self.agent_id
        if not agent:
            raise ValueError("No agent ID specified")
        
        payload = {'agent_id': agent}
        if capabilities:
            payload['capabilities'] = capabilities
        
        return self._request('POST', '/agents/heartbeat', json=payload)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List registered agents.
        
        Returns:
            List of agents
        """
        return self._request('GET', '/agents')
