"""
MCP integration hooks for YAAP LLM framework
Provides the foundation for Model Context Protocol integration
"""

from typing import List, Dict, Any, Optional, Protocol, runtime_checkable
from abc import ABC, abstractmethod


@runtime_checkable
class MCPTool(Protocol):
    """Protocol for MCP tool implementations"""
    
    name: str
    description: str
    parameters: Dict[str, Any]
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        ...


class MCPToolRegistry:
    """Registry for MCP tools that can be called by the LLM"""
    
    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
    
    def register_tool(self, tool: MCPTool) -> None:
        """Register an MCP tool"""
        self._tools[tool.name] = tool
    
    def unregister_tool(self, name: str) -> None:
        """Unregister an MCP tool"""
        self._tools.pop(name, None)
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a registered tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())
    
    def to_openai_format(self) -> List[Dict[str, Any]]:
        """Convert registered tools to OpenAI function calling format"""
        tools = []
        for tool in self._tools.values():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return tools
    
    async def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name with given parameters"""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        
        return await tool.execute(**kwargs)


class MCPManager:
    """Manager for MCP client connections and tool coordination"""
    
    def __init__(self):
        self.tool_registry = MCPToolRegistry()
        self._clients: Dict[str, Any] = {}  # Will store MCP clients
    
    def register_client(self, name: str, client: Any) -> None:
        """Register an MCP client"""
        self._clients[name] = client
    
    def unregister_client(self, name: str) -> None:
        """Unregister an MCP client"""
        self._clients.pop(name, None)
    
    def get_client(self, name: str) -> Optional[Any]:
        """Get a registered MCP client"""
        return self._clients.get(name)
    
    def list_clients(self) -> List[str]:
        """List all registered client names"""
        return list(self._clients.keys())
    
    async def sync_tools(self) -> None:
        """Sync tools from all connected MCP clients"""
        # This will be implemented when MCP client integration is added
        # For now, this is a placeholder for the future implementation
        pass
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI function calling format"""
        return self.tool_registry.to_openai_format()


# Global MCP manager instance
mcp_manager = MCPManager()


def get_mcp_manager() -> MCPManager:
    """Get the global MCP manager instance"""
    return mcp_manager