"""MCP (Model Context Protocol) client integration"""
import json
from typing import Dict, Any, Optional
import httpx


class MCPClient:
    """Client for MCP server integration"""
    
    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url
        self.client = httpx.Client(timeout=30.0)
    
    def get_tool(self, tool_name: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        Call an MCP tool on the server.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            
        Returns:
            Tool result or None if error
        """
        try:
            response = self.client.post(
                f"{self.server_url}/tools/{tool_name}",
                json=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"MCP Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"MCP Client Error: {e}")
            return None
    
    def list_tools(self) -> list:
        """List available MCP tools"""
        try:
            response = self.client.get(f"{self.server_url}/tools")
            if response.status_code == 200:
                return response.json().get("tools", [])
        except Exception as e:
            print(f"Error listing tools: {e}")
        return []
    
    def close(self):
        """Close the client"""
        self.client.close()


# Global MCP client instance
mcp_client = MCPClient()