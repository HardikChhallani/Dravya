"""
Groq services module that handles interaction with the Groq LLM API.
"""
import os
import json
from typing import Dict, List, Any, Optional

import groq
from dotenv import load_dotenv

from src.client.mcp_client import create_mcp_client
from src.utils.config import get_system_prompt

# Load environment variables
load_dotenv()

# Default model ID for Groq API
MODEL_ID = "Llama3-8b-8192"

# Retrieve Groq API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY environment variable is not set.")

# Initialize the Groq client
client = groq.Client(api_key=GROQ_API_KEY)

class GroqService:
    """
    Service class for interacting with the Groq LLM API.
    """
    
    def __init__(self):
        """Initialize the GroqService with empty tools."""
        self.tools = {}
        
    def initialize_tools(self):
        """
        Initialize and collect available MCP tools.
        
        Returns:
            Dict[str, Any]: Dictionary of available tools
        """
        tools = {}
        
        with create_mcp_client() as mcp_client:
            try:
                mcp_tools = mcp_client.get_available_tools()
                
                # Process each tool
                for tool in mcp_tools:
                    if tool.name != "list_tables":  # Skip list_tables tool
                        tools[tool.name] = {
                            "name": tool.name,
                            "callable": mcp_client.call_tool(tool.name),
                            "schema": {
                                "type": "function",
                                "function": {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                                }
                            }
                        }
            except Exception as e:
                print(f"Error setting up tools: {e}")
                
        self.tools = tools
        return tools
    
    def get_tools(self):
        """
        Get the initialized tools or initialize them if not already done.
        
        Returns:
            Dict[str, Any]: Dictionary of available tools
        """
        if not self.tools:
            return self.initialize_tools()
        return self.tools

    def generate_response(self, user_input: str, tab: str) -> Dict[str, Any]:
        """
        Generate a response to the user input using the Groq LLM,
        potentially using tools when required.
        
        Args:
            user_input (str): User's input query
            tab (str): Current tab/context for custom system prompt
            
        Returns:
            Dict[str, Any]: Response containing formatted result and raw output
        """
        tools = self.get_tools()
        
        # Get the appropriate system prompt for the current tab
        system_prompt = get_system_prompt(tab, tools)
        
        # Prepare the messages for the LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        # Query the LLM via the Groq client
        first_response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            tools=[t["schema"] for t in tools.values()] if tools else None,
            max_tokens=4096,
            temperature=0
        )

        # Check if tools need to be called
        if getattr(first_response.choices[0].message, "tool_calls", None) is not None:
            for tool_call in first_response.choices[0].message.tool_calls:
                arguments = tool_call.function.arguments
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                    
                # Execute the tool
                result = tools[tool_call.function.name]["callable"](**arguments)
                
                # Add the tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": json.dumps(result)
                })
                
            # Get a new response with the tool results
            new_response = client.chat.completions.create(
                model=MODEL_ID,
                messages=messages
            )
            response = new_response
        else:
            response = first_response

        # Return both formatted result and raw response
        return {
            "content": response.choices[0].message.content,
            "raw_response": response
        }

# Create a singleton instance of the service
groq_service = GroqService()