"""
OpenAI-compatible LLM client for YAAP
Works with OpenAI, Ollama, and other OpenAI-compatible APIs
"""

import asyncio
from typing import List, AsyncGenerator, Optional, Dict, Any
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from .base import BaseLLM, Message, LLMResponse, MessageRole
from config.settings import LLMConfig
from utils.helpers import postprocess_response, extract_thinking_content


class OpenAIClient(BaseLLM):
    """OpenAI-compatible client that works with various LLM providers"""
    
    def __init__(self, config: LLMConfig, enable_postprocessing: bool = True):
        super().__init__(config.model)
        self.config = config
        self.enable_postprocessing = enable_postprocessing
        self._client = None
        self._mcp_tools = []  # Will be populated by MCP integration
    
    @property
    def client(self) -> AsyncOpenAI:
        """Lazy initialization of OpenAI client"""
        if self._client is None:
            self._client = AsyncOpenAI(**self.config.client_kwargs)
        return self._client
    
    async def generate(
        self, 
        messages: List[Message], 
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM
        
        Args:
            messages: List of conversation messages
            stream: Whether to use streaming (for compatibility)
            **kwargs: Additional parameters for generation
            
        Returns:
            LLMResponse object with the generated content
        """
        # Prepare API parameters
        api_params = self.config.to_dict()
        api_params.update(kwargs)
        
        # Convert messages to API format
        api_messages = self.prepare_messages(messages)
        
        # Add MCP tools if available
        if self._mcp_tools:
            api_params["tools"] = self._mcp_tools
            api_params["tool_choice"] = "auto"
        
        try:
            # Make API call
            response: ChatCompletion = await self.client.chat.completions.create(
                messages=api_messages,
                **api_params
            )
            
            # Extract response data
            message = response.choices[0].message
            content = message.content or ""
            
            # Handle tool calls if present
            if hasattr(message, 'tool_calls') and message.tool_calls:
                content = await self._handle_tool_calls(message.tool_calls, content)
            
            # Apply postprocessing if enabled
            if self.enable_postprocessing:
                content = postprocess_response(content, remove_thinking=True)
            
            return LLMResponse(
                content=content,
                model=response.model,
                usage=response.usage.model_dump() if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "response_id": response.id,
                    "created": response.created,
                }
            )
            
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}") from e
    
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
        # Prepare API parameters
        api_params = self.config.to_dict()
        api_params.update(kwargs)
        api_params["stream"] = True
        
        # Convert messages to API format
        api_messages = self.prepare_messages(messages)
        
        # Add MCP tools if available
        if self._mcp_tools:
            api_params["tools"] = self._mcp_tools
            api_params["tool_choice"] = "auto"
        
        try:
            # Make streaming API call
            stream = await self.client.chat.completions.create(
                messages=api_messages,
                **api_params
            )
            
            if self.enable_postprocessing:
                # Buffer the entire response for postprocessing
                full_response = ""
                async for chunk in stream:
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        if delta.content:
                            full_response += delta.content
                
                # Apply postprocessing to the full response
                processed_response = postprocess_response(full_response, remove_thinking=True)
                
                # Yield the processed response as a single chunk
                if processed_response:
                    yield processed_response
            else:
                # Stream without postprocessing
                async for chunk in stream:
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        if delta.content:
                            yield delta.content
                        
        except Exception as e:
            raise RuntimeError(f"LLM streaming failed: {str(e)}") from e
    
    def register_mcp_tools(self, tools: List[Dict[str, Any]]) -> None:
        """
        Register MCP tools for function calling
        
        Args:
            tools: List of MCP tool definitions in OpenAI format
        """
        self._mcp_tools = tools
    
    def set_postprocessing(self, enabled: bool) -> None:
        """
        Enable or disable response postprocessing
        
        Args:
            enabled: Whether to enable postprocessing
        """
        self.enable_postprocessing = enabled
    
    def extract_thinking_from_response(self, response_content: str) -> Optional[str]:
        """
        Extract thinking content from a response for debugging
        
        Args:
            response_content: Raw response content that may contain thinking tokens
            
        Returns:
            Extracted thinking content or None if no thinking tokens found
        """
        return extract_thinking_content(response_content)
    
    async def _handle_tool_calls(self, tool_calls, content: str) -> str:
        """
        Handle tool calls from the LLM (MCP integration point)
        
        Args:
            tool_calls: Tool calls from the LLM response
            content: Original response content
            
        Returns:
            Updated content with tool results
        """
        # This will be implemented when MCP integration is added
        # For now, just return the original content
        return content
    
    def prepare_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Convert Message objects to OpenAI API format"""
        api_messages = []
        
        for msg in messages:
            # Handle system messages
            if msg.role == MessageRole.SYSTEM:
                if self.supports_system_messages:
                    api_messages.append({
                        "role": "system",
                        "content": msg.content
                    })
                else:
                    # Prepend system message to first user message
                    if api_messages and api_messages[-1]["role"] == "user":
                        api_messages[-1]["content"] = f"{msg.content}\n\n{api_messages[-1]['content']}"
                    else:
                        api_messages.append({
                            "role": "user",
                            "content": msg.content
                        })
            else:
                api_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        return api_messages