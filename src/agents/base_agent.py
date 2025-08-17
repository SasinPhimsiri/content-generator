"""Base agent class for the multi-agent content generation system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger

from ..core.ollama_client import ollama_client
from ..core.config import config


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.agent_config = config.agents.get(agent_name, {})
        self.model = self.agent_config.get("model", config.ollama.model)
        self.temperature = self.agent_config.get("temperature", 0.7)
        self.max_tokens = self.agent_config.get("max_tokens", 1000)
        self.system_prompt = self.agent_config.get("system_prompt", "")
        
        logger.info(f"Initialized {self.agent_name} agent")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results."""
        pass
    
    async def generate_response(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response using the Ollama client."""
        try:
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens if max_tokens is not None else self.max_tokens
            
            result = await ollama_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=temp,
                max_tokens=tokens
            )
            
            return result.get("content", "")
        
        except Exception as e:
            logger.error(f"Error generating response for {self.agent_name}: {e}")
            raise
    
    def format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with provided variables."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable for {self.agent_name}: {e}")
            raise ValueError(f"Missing template variable: {e}")
    
    def log_activity(self, activity: str, details: Optional[Dict[str, Any]] = None):
        """Log agent activity."""
        log_message = f"{self.agent_name}: {activity}"
        if details:
            log_message += f" - {details}"
        logger.info(log_message)
