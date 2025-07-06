"""
title: OpenWebUI Tool Template
description: Complete template for creating OpenWebUI tools with best practices and common patterns
version: 2.0.0
license: MIT
requirements: requests==2.31.0, aiohttp==3.9.0, pydantic>=1.8.0
"""

# =============================================================================
# IMPORTS SECTION
# =============================================================================
import logging
import time
import asyncio
import aiohttp
from typing import Optional, Dict, Any, Callable, List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

# =============================================================================
# EVENT EMITTER SECTION
# =============================================================================

class EventEmitter:
    """
    Event emitter for progress updates and status notifications.
    
    This class provides a standardized way to send progress updates,
    error messages, and success notifications to the OpenWebUI interface.
    """
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def progress_update(self, description: str):
        """Send a progress update"""
        await self.emit(description)

    async def error_update(self, description: str):
        """Send an error update"""
        await self.emit(description, "error", True)

    async def success_update(self, description: str):
        """Send a success update"""
        await self.emit(description, "success", True)

    async def emit(self, description="Unknown State", status="in_progress", done=False):
        """Emit an event to the UI"""
        if self.event_emitter:
            await self.event_emitter(
                {
                    "type": "status",
                    "data": {
                        "status": status,
                        "description": description,
                        "done": done,
                    },
                }
            )

# =============================================================================
# MAIN TOOLS CLASS
# =============================================================================

class Tools:
    """
    Main Tools Class for OpenWebUI
    
    This is the primary class that contains all your tool methods. Each method
    in this class becomes a callable tool function that the AI can use.
    
    CRITICAL REQUIREMENTS:
    1. The class MUST be named exactly "Tools"
    2. The Valves class MUST be nested inside the Tools class
    3. Initialize valves in __init__ method
    4. Each method should have proper type hints and Pydantic Field descriptions
    5. Include comprehensive docstrings with clear usage instructions
    6. Handle errors gracefully with proper error messages
    7. Return meaningful results with appropriate data types
    
    SPECIAL PARAMETERS (automatically injected by OpenWebUI):
    - __user__: dict - Current user information
    - __id__: str - Tool instance ID
    - __event_emitter__: Callable - For progress updates
    - __messages__: list - Conversation history
    
    These special parameters should NOT be documented in your tool specifications.
    """
    
    class Valves(BaseModel):
        """
        Tool-level configuration (Valves) - NESTED INSIDE Tools class
        
        This class defines configuration that applies to ALL users of this tool.
        These settings are stored in the database and shared across all tool instances.
        
        IMPORTANT: This class MUST be nested inside the Tools class for proper initialization.
        
        Use this for:
        - API keys that are the same for all users
        - Base URLs for external services
        - Global tool settings
        - Default configurations
        - Rate limiting settings
        - Timeout configurations
        """
        
        # API Configuration
        api_key: Optional[str] = Field(
            default=None, 
            description="API key for external service (required for functionality)"
        )
        base_url: str = Field(
            default="https://api.example.com", 
            description="Base URL for API calls"
        )
        timeout: int = Field(
            default=30, 
            description="Request timeout in seconds"
        )
        
        # Rate Limiting
        max_requests_per_minute: int = Field(
            default=60, 
            description="Maximum requests per minute"
        )
        max_retries: int = Field(
            default=3, 
            description="Number of retry attempts for failed requests"
        )
        
        # Feature Flags
        enable_caching: bool = Field(
            default=True, 
            description="Enable response caching"
        )
        debug_mode: bool = Field(
            default=False, 
            description="Enable debug logging"
        )
        citation: bool = Field(
            default=False, 
            description="Include citation in responses. When False, returns exact tool output. When True, adds attribution formatting."
        )
        
        @validator('api_key')
        def validate_api_key(cls, v):
            """Validate API key is provided if required"""
            if not v:
                raise ValueError('API key is required for this tool functionality')
            return v
        
        @validator('timeout')
        def validate_timeout(cls, v):
            """Validate timeout is reasonable"""
            if v < 1 or v > 3600:
                raise ValueError('Timeout must be between 1 and 3600 seconds (1 second to 1 hour)')
            return v
        
        @validator('max_requests_per_minute')
        def validate_rate_limit(cls, v):
            """Validate rate limit is reasonable"""
            if v < 1 or v > 1000:
                raise ValueError('Rate limit must be between 1 and 1000 requests per minute')
            return v
        
        @validator('max_retries')
        def validate_max_retries(cls, v):
            """Validate retry count is reasonable"""
            if v < 0 or v > 10:
                raise ValueError('Max retries must be between 0 and 10')
            return v

    def __init__(self):
        """
        Initialize the Tool
        
        CRITICAL: This method MUST initialize the valves instance.
        The valves are automatically loaded by OpenWebUI when the tool is first used.
        """
        self.valves = self.Valves()
        self.citation = self.valves.citation
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"{self.__class__.__name__} initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get an aiohttp session with proper timeout configuration.
        
        Returns:
            aiohttp.ClientSession: Configured session
        """
        timeout = aiohttp.ClientTimeout(total=self.valves.timeout)
        return aiohttp.ClientSession(timeout=timeout)
    
    def _log_request(self, method: str, url: str, params: dict = None):
        """Log API request for debugging"""
        if self.valves.debug_mode:
            self.logger.info(f"API Request: {method} {url}")
            if params:
                self.logger.debug(f"Parameters: {params}")
    
    def _handle_error(self, error: Exception, context: str = "") -> str:
        """
        Handle errors gracefully and return user-friendly error messages.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            str: User-friendly error message
        """
        error_msg = f"Error {context}: {str(error)}"
        self.logger.error(error_msg)
        return error_msg
    
    async def example_tool_method(
        self,
        input_data: str = Field(..., description="CRITICAL: Use the EXACT user input without ANY modifications, rephrasing, or adjustments. Pass the user's input verbatim."),
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
        __messages__: list = None,
    ) -> str:
        """
        Example tool method demonstrating best practices.
        
        CRITICAL INSTRUCTION: This tool MUST use the user's original input EXACTLY as provided,
        without any modifications, rephrasing, or adjustments. The input_data parameter should be
        passed verbatim to any external APIs. Do not:
        - Rephrase or reword the user's input
        - Add context or explanations
        - Modify the language or structure
        - Expand or condense the original input
        
        Use this tool when you need to process user input in a specific way.
        This is particularly useful for:
        - Data processing tasks
        - API calls that require exact user input
        - Text analysis and manipulation
        - External service integration
        
        Args:
            input_data: The user's original input (use exactly as provided)
            __event_emitter__: Event emitter for progress updates (auto-injected)
            __user__: Current user information (auto-injected)
            __messages__: Conversation history (auto-injected)
            
        Returns:
            str: Processed result or error message
        """
        # Initialize event emitter
        emitter = EventEmitter(__event_emitter__)
        
        try:
            await emitter.progress_update("Processing input...")
            
            # Validate required configuration
            if not self.valves.api_key:
                error_msg = "API key is required. Please configure it in the tool settings."
                await emitter.error_update(error_msg)
                return error_msg
            
            # CRITICAL: Use the original user input exactly as provided - NO modifications allowed
            # The model should pass the user's input verbatim without any rephrasing
            processed_input = input_data  # EXACT original user input - DO NOT MODIFY
            
            await emitter.progress_update("Making API request...")
            
            # Example API call with retry logic
            timeout = aiohttp.ClientTimeout(total=self.valves.timeout)
            last_error = None
            
            for attempt in range(self.valves.max_retries + 1):
                try:
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        # Example API call
                        async with session.post(
                            f"{self.valves.base_url}/example",
                            json={"input": processed_input},
                            headers={"Authorization": f"Bearer {self.valves.api_key}"}
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                await emitter.success_update("Processing completed successfully!")
                                return data.get("result", "No result returned")
                            else:
                                error_text = await response.text()
                                last_error = f"API request failed with status {response.status}: {error_text}"
                                
                                # Don't retry on client errors (4xx)
                                if 400 <= response.status < 500:
                                    await emitter.error_update(last_error)
                                    return last_error
                                
                                # Retry on server errors (5xx) or network issues
                                if attempt < self.valves.max_retries:
                                    await emitter.progress_update(f"Request failed, retrying... (attempt {attempt + 1}/{self.valves.max_retries + 1})")
                                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                    continue
                                else:
                                    await emitter.error_update(last_error)
                                    return last_error
                                    
                except asyncio.TimeoutError:
                    last_error = f"Request timed out after {self.valves.timeout} seconds"
                    if attempt < self.valves.max_retries:
                        await emitter.progress_update(f"Request timed out, retrying... (attempt {attempt + 1}/{self.valves.max_retries + 1})")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        await emitter.error_update(last_error)
                        return last_error
                        
            # If we get here, all retries failed
            await emitter.error_update(last_error or "All retry attempts failed")
            return last_error or "All retry attempts failed"
            
        except Exception as e:
            error_msg = self._handle_error(e, "during processing")
            await emitter.error_update(error_msg)
            return error_msg
    
    async def cleanup(self):
        """
        Cleanup method called when the tool is unloaded.
        
        Use this for:
        - Closing database connections
        - Cleaning up temporary files
        - Saving any pending data
        - Logging cleanup completion
        """
        self.logger.info(f"{self.__class__.__name__} cleanup completed") 