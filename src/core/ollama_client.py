"""Ollama client for interacting with local LLM models."""

import json
from typing import Dict, Any, Optional, AsyncGenerator
import asyncio
import httpx
from loguru import logger

from .config import config


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self):
        self.base_url = config.ollama.base_url
        self.model = config.ollama.model
        self.timeout = 300.0  # 5 minutes for larger models
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate text using Ollama."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": stream,
                    "options": {
                        "temperature": temperature,
                    }
                }
                
                if system_prompt:
                    payload["system"] = system_prompt
                
                if max_tokens:
                    payload["options"]["num_predict"] = max_tokens
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                
                if stream:
                    return response
                else:
                    result = response.json()
                    return {
                        "content": result.get("response", ""),
                        "model": result.get("model", self.model),
                        "done": result.get("done", True)
                    }
        
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {e}")
            raise
    
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Stream text generation from Ollama."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                    }
                }
                
                if system_prompt:
                    payload["system"] = system_prompt
                
                if max_tokens:
                    payload["options"]["num_predict"] = max_tokens
                
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
        
        except Exception as e:
            logger.error(f"Error streaming text from Ollama: {e}")
            raise
    
    async def check_model_availability(self) -> bool:
        """Check if the specified model is available."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                
                return self.model in available_models
        
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    async def pull_model(self) -> bool:
        """Pull the specified model if not available."""
        try:
            async with httpx.AsyncClient(timeout=600.0) as client:
                payload = {"name": self.model}
                
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json=payload
                )
                response.raise_for_status()
                
                logger.info(f"Successfully pulled model: {self.model}")
                return True
        
        except Exception as e:
            logger.error(f"Error pulling model {self.model}: {e}")
            return False


# Global Ollama client instance
ollama_client = OllamaClient()
