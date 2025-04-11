"""
MCP Client module that provides a synchronous wrapper around the asynchronous MCP client.
"""
import os
import sys
import asyncio
from typing import Any, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClientSync:
    """
    Synchronous MCP client that wraps asynchronous operations in a single event loop.
    
    This class provides a synchronous interface to the asynchronous MCP client,
    making it easier to use in non-async contexts like Streamlit.
    """
    def __init__(self, server_params: StdioServerParameters):
        """
        Initialize the MCP client with server parameters.
        
        Args:
            server_params (StdioServerParameters): Parameters for the MCP server connection
        """
        self.server_params = server_params
        self.session = None
        self._client = None
        self.read = None
        self.write = None
        self._loop = None

    def __enter__(self):
        """
        Set up the asyncio event loop and initialize the MCP client session.
        
        Returns:
            MCPClientSync: The initialized client instance
        """
        # Set up an appropriate event loop based on the platform
        if sys.platform == 'win32':
            self._loop = asyncio.ProactorEventLoop()
        else:
            self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        async def setup():
            self._client = stdio_client(self.server_params)
            self.read, self.write = await self._client.__aenter__()
            session = ClientSession(self.read, self.write)
            self.session = await session.__aenter__()
            await self.session.initialize()
        
        self._loop.run_until_complete(setup())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Clean up the resources when exiting the context manager.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if not self._loop:
            return
            
        async def cleanup():
            try:
                if self.session:
                    await self.session.__aexit__(exc_type, exc_val, exc_tb)
                if self._client:
                    await self._client.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                print(f"Cleanup error: {e}")
                
        try:
            self._loop.run_until_complete(cleanup())
        finally:
            self._loop.close()
            
    def get_available_tools(self) -> List[Any]:
        """
        Get the list of available tools from the MCP server.
        
        Returns:
            List[Any]: List of available tools
            
        Raises:
            RuntimeError: If not connected to the MCP server
        """
        if not self.session or not self._loop:
            raise RuntimeError("Not connected to the MCP server")
        
        async def get_tools():
            tools_data = await self.session.list_tools()
            return tools_data.tools if hasattr(tools_data, 'tools') else []
        
        return self._loop.run_until_complete(get_tools())

    def call_tool(self, tool_name: str):
        """
        Returns a callable function to execute the given MCP tool.
        
        Args:
            tool_name (str): Name of the tool to call
            
        Returns:
            callable: Function that will execute the tool when called
            
        Raises:
            RuntimeError: If not connected to the MCP server
        """
        if not self.session or not self._loop:
            raise RuntimeError("Not connected to the MCP server")

        def callable_function(*args, **kwargs):
            async def run_tool():
                response = await self.session.call_tool(tool_name, arguments=kwargs)
                return response.content[0].text
            return self._loop.run_until_complete(run_tool())

        return callable_function

def create_mcp_client():
    """
    Creates and configures an MCP client with Eka credentials from environment variables.
    
    Returns:
        MCPClientSync: Configured MCP client instance
        
    Raises:
        EnvironmentError: If required environment variables are not set
    """
    # Get Eka credentials from environment
    eka_client_id = os.getenv("EKA_CLIENT_ID")
    eka_client_secret = os.getenv("EKA_CLIENT_SECRET")
    
    if not eka_client_id or not eka_client_secret:
        raise EnvironmentError("EKA_CLIENT_ID or EKA_CLIENT_SECRET environment variables are not set.")

    # Configure the server parameters
    server_params = StdioServerParameters(
        command="uvx",
        args=[
            "eka_mcp_server",
            "--eka-api-host", "https://api.eka.care",
            "--client-id", eka_client_id,
            "--client-secret", eka_client_secret
        ],
        env=None
    )
    
    return MCPClientSync(server_params)