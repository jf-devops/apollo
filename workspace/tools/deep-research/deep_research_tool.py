"""
title: Deep Research Tool
author: Brian Zelun Jin
description: Deep research tool using OpenAI's o3-deep-research model for comprehensive investigation. This is a workaround to access the o3-deep-research model which uses the new responses API endpoint.
version: 1.0.0
license: MIT
requirements: openai==1.0.0, aiohttp==3.9.0, pydantic>=1.8.0
"""

# =============================================================================
# IMPORTS SECTION
# =============================================================================
import logging
import time
import aiohttp
import asyncio
from typing import Optional, Dict, Any, Callable
from pydantic import BaseModel, Field, validator
from datetime import datetime

# =============================================================================
# EVENT EMITTER SECTION
# =============================================================================

class EventEmitter:
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def progress_update(self, description):
        await self.emit(description)

    async def error_update(self, description):
        await self.emit(description, "error", True)

    async def success_update(self, description):
        await self.emit(description, "success", True)

    async def emit(self, description="Unknown State", status="in_progress", done=False):
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
    Deep Research Tool using OpenAI's o3-deep-research model
    
    This tool provides access to OpenAI's deep research capabilities
    for comprehensive investigation of user queries.
    """
    
    class Valves(BaseModel):
        """
        Tool-level configuration (shared across all users)
        
        Configuration for OpenAI o3-deep-search API integration.
        """
        
        api_key: Optional[str] = Field(
            default=None, 
            description="OpenAI API key (required for deep search functionality)"
        )
        base_url: str = Field(
            default="https://api.openai.com/v1", 
            description="OpenAI API base URL"
        )
        timeout: int = Field(
            default=1800,  # 30 minutes in seconds
            description="Request timeout in seconds (deep search can take up to 20 minutes)"
        )
        model_name: str = Field(
            default="o3-deep-research", 
            description="Deep search model name"
        )
        max_retries: int = Field(
            default=3, 
            description="Number of retry attempts for failed requests"
        )
        citation: bool = Field(
            default=False, 
            description="Include citation in responses. When False, returns exact tool output. When True, adds attribution formatting."
        )
        
        @validator('api_key')
        def validate_api_key(cls, v):
            """Validate API key is provided"""
            if not v:
                raise ValueError('API key is required for deep search functionality')
            return v
        
        @validator('timeout')
        def validate_timeout(cls, v):
            """Validate timeout is reasonable for deep search"""
            if v < 60 or v > 3600:  # Between 1 minute and 1 hour
                raise ValueError('Timeout must be between 60 and 3600 seconds (1 minute to 1 hour)')
            return v
        
        @validator('max_retries')
        def validate_max_retries(cls, v):
            """Validate retry count is reasonable"""
            if v < 0 or v > 10:
                raise ValueError('Max retries must be between 0 and 10')
            return v

    def __init__(self):
        """
        Initialize the Deep Search Tool
        """
        self.valves = self.Valves()
        self.citation = self.valves.citation
        self.logger = logging.getLogger(__name__)
        self.logger.info("Deep Research Tool initialized")
    
    async def perform_deep_research(
        self,
        message: str = Field(..., description="CRITICAL: Use the EXACT original user message/query without ANY modifications, rephrasing, or adjustments. Pass the user's message verbatim to the API."),
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
        __messages__: list = None,
    ) -> str:
        """
        Perform deep research using OpenAI's o3-deep-research model for comprehensive investigation.
        
        CRITICAL INSTRUCTION: This tool MUST use the user's original message EXACTLY as provided,
        without any modifications, rephrasing, or adjustments. The message parameter should be
        passed verbatim to the OpenAI API. Do not:
        - Rephrase or reword the user's query
        - Add context or explanations
        - Modify the language or structure
        - Expand or condense the original message
        
        Use this tool when a user asks for in-depth research, investigation, or comprehensive analysis
        of a topic. This is particularly useful for:
        - Research requests ("research", "investigate", "find out about")
        - Complex topics requiring deep analysis
        - Current events and developments
        - Technical or scientific questions
        - Comparative analysis ("compare", "analyze differences")
        - Questions requiring comprehensive investigation
        
        This method takes a user's query and sends it to OpenAI's deep research
        API for comprehensive investigation. It returns the research results
        with clear attribution that deep research was utilized.
        
        :param message: The user's original message/query to research
        :param __event_emitter__: Event emitter for UI feedback
        :param __user__: User context and settings
        :param __messages__: Full conversation history
        :return: Deep research results with attribution
        """
        emitter = EventEmitter(__event_emitter__)
        
        # Get the original user message from conversation history
        original_user_message = message
        if __messages__ and len(__messages__) > 0:
            # Find the last user message in the conversation
            for msg in reversed(__messages__):
                if msg.get("role") == "user":
                    original_user_message = msg.get("content", message)
                    break
        
        try:
            await emitter.progress_update("Initializing deep research...")
            
            # Validate API key
            if not self.valves.api_key:
                error_msg = "OpenAI API key is required. Please configure it in the tool settings."
                await emitter.error_update(error_msg)
                return error_msg
            
            await emitter.progress_update("Preparing deep research request...")
            
            # CRITICAL: Use the original user message exactly as provided - NO modifications allowed
            # The model should pass the user's query verbatim to the API without any rephrasing
            payload = {
                "model": self.valves.model_name,
                "input": original_user_message,  # EXACT original user message - DO NOT MODIFY
                "tools": [
                    {
                        "type": "web_search_preview"
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.valves.api_key}",
                "Content-Type": "application/json"
            }
            
            await emitter.progress_update("Sending request to OpenAI responses API...")
            
            # Make the API request to responses endpoint with retry logic
            timeout = aiohttp.ClientTimeout(total=self.valves.timeout)
            last_error = None
            
            for attempt in range(self.valves.max_retries + 1):
                try:
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(
                            f"{self.valves.base_url}/responses",
                            json=payload,
                            headers=headers
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # Extract the response content from the output array
                                research_results = ""
                                if "output" in data:
                                    for output_item in data["output"]:
                                        if output_item.get("type") == "message" and "content" in output_item:
                                            for content_item in output_item["content"]:
                                                if content_item.get("type") == "output_text":
                                                    research_results += content_item.get("text", "")
                                
                                # Fallback to text field if output parsing fails
                                if not research_results and "text" in data:
                                    research_results = data.get("text", "")
                                
                                await emitter.success_update("Deep research completed successfully!")
                                
                                # Return the raw research results directly
                                return research_results
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
            
        except asyncio.TimeoutError:
            error_msg = f"Request timed out after {self.valves.timeout} seconds"
            await emitter.error_update(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error during deep search: {str(e)}"
            await emitter.error_update(error_msg)
            return error_msg
    
    async def cleanup(self):
        """
        Cleanup method called when the tool is unloaded
        """
        self.logger.info("Deep Research Tool cleanup completed")


