"""
Base LLM interface for YAAP
Provides abstract base class for all LLM implementations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum


class MessageRole(Enum):
    """Message roles for conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """Represents a conversation message"""
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Response from LLM with metadata"""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLM(ABC):
    """Abstract base class for all LLM implementations"""
    
    def __init__(self, model: str, **kwargs):
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    async def generate(
        self, 
        messages: List[Message], 
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters for generation
            
        Returns:
            LLMResponse object with the generated content
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self, 
        messages: List[Message], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the LLM
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters for generation
            
        Yields:
            String chunks of the response
        """
        pass
    
    def create_message(self, role: MessageRole, content: str, **metadata) -> Message:
        """Helper method to create a Message object"""
        return Message(role=role, content=content, metadata=metadata)
    
    @property
    def supports_streaming(self) -> bool:
        """Whether this LLM implementation supports streaming"""
        return True
    
    @property
    def supports_system_messages(self) -> bool:
        """Whether this LLM implementation supports system messages"""
        return True
    
    def prepare_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Convert Message objects to API format"""
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]