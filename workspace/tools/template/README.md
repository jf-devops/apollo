# OpenWebUI Tool Template

This directory contains a comprehensive template for creating OpenWebUI tools. The template provides all the necessary structure, documentation, and examples to help you build robust and feature-rich tools.

## 📁 Files

- `tool_template.py` - The main template file with comprehensive examples and documentation
- `README.md` - This file with additional guidance and best practices

## 🚀 Quick Start

1. **Copy the template**: Copy `tool_template.py` to create your new tool
2. **Customize the frontmatter**: Update the requirements, description, version, etc.
3. **Replace example methods**: Replace the example methods with your actual functionality
4. **Configure Valves**: Set up appropriate configuration models (nested inside Tools class)
5. **Test thoroughly**: Test all methods before deployment
6. **Deploy**: Upload your tool to OpenWebUI

## ⚠️ CRITICAL REQUIREMENTS

### 1. Class Structure
- **MUST** name the main class exactly `Tools`
- **MUST** nest the `Valves` class inside the `Tools` class
- **MUST** initialize valves in the `__init__` method

### 2. Input Handling
- **CRITICAL**: Use the user's original input EXACTLY as provided
- **DO NOT** modify, rephrase, or adjust user input
- **DO NOT** add context or explanations to user input
- Pass user input verbatim to external APIs

### 3. Special Parameters
These are automatically injected by OpenWebUI and should NOT be documented in tool specifications:
- `__user__: dict` - Current user information
- `__id__: str` - Tool instance ID  
- `__event_emitter__: Callable` - For progress updates
- `__messages__: list` - Conversation history

## 📋 Template Structure

### 1. Frontmatter Section
```python
"""
title: Your Tool Name
description: Brief description of what your tool does
version: 1.0.0
license: MIT
requirements: package1==1.0.0, package2==2.0.0
"""
```

### 2. Imports Section
```python
import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any, Callable
from pydantic import BaseModel, Field, validator
```

### 3. Event Emitter (Optional)
```python
class EventEmitter:
    """For progress updates and status notifications"""
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter
    
    async def progress_update(self, description: str):
        await self.emit(description)
```

### 4. Main Tools Class with Nested Valves
```python
class Tools:
    class Valves(BaseModel):
        """Tool-level configuration - NESTED INSIDE Tools class"""
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
        citation: bool = Field(
            default=False, 
            description="Include citation in responses. When False, returns exact tool output."
        )
        
        @validator('api_key')
        def validate_api_key(cls, v):
            if not v:
                raise ValueError('API key is required for this tool functionality')
            return v

    def __init__(self):
        """CRITICAL: Initialize valves instance"""
        self.valves = self.Valves()
        self.citation = self.valves.citation
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"{self.__class__.__name__} initialized")
    
    async def your_tool_method(
        self,
        input_data: str = Field(..., description="CRITICAL: Use the EXACT user input without ANY modifications, rephrasing, or adjustments. Pass the user's input verbatim."),
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
        __messages__: list = None,
    ) -> str:
        """
        Description of what this tool does.
        
        CRITICAL INSTRUCTION: This tool MUST use the user's original input EXACTLY as provided,
        without any modifications, rephrasing, or adjustments. The input_data parameter should be
        passed verbatim to any external APIs. Do not:
        - Rephrase or reword the user's input
        - Add context or explanations
        - Modify the language or structure
        - Expand or condense the original input
        
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
            
            # CRITICAL: Use the original user input exactly as provided - NO modifications allowed
            processed_input = input_data  # EXACT original user input - DO NOT MODIFY
            
            # Your implementation here
            return "Result"
            
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            await emitter.error_update(error_msg)
            return error_msg
    
    async def cleanup(self):
        """Cleanup method called when the tool is unloaded"""
        self.logger.info(f"{self.__class__.__name__} cleanup completed")
```

## 🔧 Key Components Explained

### Valves (Tool-level Configuration)
- **MUST** be nested inside the `Tools` class
- Shared across all users of the tool
- Stored in the database
- Good for: API keys, base URLs, global settings, timeouts, retry logic
- Example: Service API key, default endpoints, rate limiting

### Event Emitter
- Provides progress updates to the OpenWebUI interface
- Use for long-running operations
- Methods: `progress_update()`, `error_update()`, `success_update()`

### Citation Behavior
- `citation=False` (default): Tool output is directly injected into conversation
- `citation=True`: Tool output is treated as a citation/reference
- Controls whether the model sees the exact tool output or just a reference

## 📝 Method Requirements

Every tool method must have:

1. **Type hints** for all parameters
2. **Pydantic Field** with clear descriptions (especially for input parameters)
3. **CRITICAL instructions** about using exact user input
4. **Comprehensive docstrings** with usage instructions
5. **Proper error handling** with user-friendly messages
6. **Event emitter integration** for progress updates
7. **Meaningful return values**

## 🔒 Security Best Practices

1. **Input Validation**: Always validate and sanitize inputs
2. **API Key Management**: Store sensitive data in Valves
3. **Rate Limiting**: Implement rate limiting for API calls
4. **Error Messages**: Don't expose sensitive information in error messages
5. **Timeout Configuration**: Set appropriate timeouts for external calls

## 🚀 Performance Tips

1. **Async Operations**: Use async/await for I/O operations
2. **Session Reuse**: Reuse HTTP sessions for multiple requests
3. **Retry Logic**: Implement exponential backoff for failed requests
4. **Resource Cleanup**: Always clean up resources in the cleanup method
5. **Progress Updates**: Use event emitter for long-running operations

## 🧪 Testing Guidelines

1. **Unit Tests**: Test each method individually
2. **Integration Tests**: Test the tool as a whole
3. **Error Scenarios**: Test error conditions and edge cases
4. **Input Validation**: Test with various input types and edge cases
5. **API Integration**: Test external API calls and error handling

## 📊 Common Patterns

### API Integration with Retry Logic
```python
async def api_call(self, endpoint: str, data: dict = None) -> str:
    emitter = EventEmitter(__event_emitter__)
    
    for attempt in range(self.valves.max_retries + 1):
        try:
            async with aiohttp.ClientSession(timeout=self.valves.timeout) as session:
                async with session.post(endpoint, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        # Don't retry on client errors (4xx)
                        if 400 <= response.status < 500:
                            return f"API error: {response.status}"
                        
                        # Retry on server errors (5xx)
                        if attempt < self.valves.max_retries:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
        except asyncio.TimeoutError:
            if attempt < self.valves.max_retries:
                await asyncio.sleep(2 ** attempt)
                continue
            return "Request timed out"
    
    return "All retry attempts failed"
```

### Input Processing Pattern
```python
async def process_input(
    self,
    user_input: str = Field(..., description="CRITICAL: Use the EXACT user input without ANY modifications, rephrasing, or adjustments. Pass the user's input verbatim."),
    __event_emitter__: Callable[[dict], Any] = None,
    __user__: dict = {},
    __messages__: list = None,
) -> str:
    """
    Process user input exactly as provided.
    
    CRITICAL INSTRUCTION: This tool MUST use the user's original input EXACTLY as provided,
    without any modifications, rephrasing, or adjustments.
    """
    emitter = EventEmitter(__event_emitter__)
    
    try:
        # CRITICAL: Use the original user input exactly as provided - NO modifications allowed
        processed_input = user_input  # EXACT original user input - DO NOT MODIFY
        
        await emitter.progress_update("Processing input...")
        
        # Your processing logic here
        result = await self._process_exact_input(processed_input)
        
        await emitter.success_update("Processing completed!")
        return result
        
    except Exception as e:
        error_msg = f"Error during processing: {str(e)}"
        await emitter.error_update(error_msg)
        return error_msg
```

## 🔧 Advanced Features

### Conversation History Access
```python
async def method_with_history(
    self,
    current_input: str = Field(..., description="Current user input"),
    __messages__: list = None,
) -> str:
    """Access conversation history for context"""
    if __messages__ and len(__messages__) > 0:
        # Find the last user message
        for msg in reversed(__messages__):
            if msg.get("role") == "user":
                original_user_message = msg.get("content", current_input)
                break
    else:
        original_user_message = current_input
    
    # Use original_user_message for processing
    return f"Processing: {original_user_message}"
```

### Configuration Validation
```python
class Valves(BaseModel):
    api_key: Optional[str] = Field(default=None, description="API key")
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v:
            raise ValueError('API key is required for this tool functionality')
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v < 1 or v > 3600:
            raise ValueError('Timeout must be between 1 and 3600 seconds')
        return v
```

## 🚨 Common Pitfalls

1. **Not nesting Valves class**: Must be inside Tools class
2. **Modifying user input**: Always use exact user input
3. **Missing initialization**: Must initialize valves in __init__
4. **Poor error handling**: Always provide user-friendly error messages
5. **No progress updates**: Use event emitter for long operations
6. **Missing cleanup**: Always implement cleanup method

## 📚 Additional Resources

- [OpenWebUI Documentation](https://docs.openwebui.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [Python Async/Await Guide](https://docs.python.org/3/library/asyncio.html)

## 🤝 Contributing

When contributing tools to the community:

1. Follow the template structure
2. Include comprehensive documentation
3. Add proper error handling
4. Test thoroughly
5. Include usage examples
6. Follow security best practices
7. Add appropriate tags and categories

## 📞 Support

If you need help with tool development:

1. Check the OpenWebUI documentation
2. Review the template examples
3. Look at existing community tools
4. Ask questions in the community forums
5. Report issues with detailed information

---

**Happy Tool Building! 🛠️**

This template is designed to help you create robust, secure, and well-documented tools for OpenWebUI. Customize it according to your needs while maintaining the established patterns and best practices. 