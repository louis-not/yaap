"""
LLM module for YAAP - Yet Another AI Program
Provides LLM integration with support for various providers
"""

from .base import BaseLLM, LLMResponse, Message, MessageRole
from .openai_client import OpenAIClient
from .mcp_integration import MCPManager, MCPTool, get_mcp_manager

__all__ = [
    'BaseLLM', 
    'LLMResponse', 
    'Message', 
    'MessageRole',
    'OpenAIClient',
    'MCPManager',
    'MCPTool',
    'get_mcp_manager'
]