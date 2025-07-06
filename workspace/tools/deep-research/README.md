# Deep Research Tool

A powerful OpenWebUI tool that provides access to OpenAI's o3-deep-research model for comprehensive investigation and research capabilities.

## 🎯 Overview

The Deep Research Tool is a workaround solution to access OpenAI's o3-deep-research model, which uses the new responses API endpoint. This tool enables users to perform in-depth research, investigation, and comprehensive analysis of topics through OpenAI's advanced research capabilities.

## ✨ Features

- **Deep Research**: Access to OpenAI's o3-deep-research model for comprehensive investigation
- **Web Search Integration**: Built-in web search preview capabilities
- **Progress Updates**: Real-time progress notifications during long-running research
- **Retry Logic**: Robust error handling with exponential backoff
- **Configurable Timeouts**: Support for long-running research operations (up to 30 minutes)
- **Exact Input Preservation**: Uses user's original query exactly as provided
- **Direct Output**: Returns research results directly to the conversation

## 🔧 Configuration

### Required Settings

The tool requires the following configuration in the Valves:

- **API Key**: Your OpenAI API key (required)
- **Base URL**: OpenAI API base URL (default: https://api.openai.com/v1)
- **Timeout**: Request timeout in seconds (default: 1800 seconds / 30 minutes)
- **Model Name**: Deep research model (default: o3-deep-research)
- **Max Retries**: Number of retry attempts (default: 3)
- **Citation**: Whether to include citation formatting (default: False)

### Valve Configuration

```python
class Valves(BaseModel):
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
        description="Include citation in responses. When False, returns exact tool output."
    )
```

## 🚀 Usage

### When to Use

Use this tool when a user asks for:
- **Research requests**: "research", "investigate", "find out about"
- **Complex topics**: Requiring deep analysis and investigation
- **Current events**: Recent developments and news analysis
- **Technical questions**: Scientific or technical topics
- **Comparative analysis**: "compare", "analyze differences"
- **Comprehensive investigation**: Questions requiring thorough research

### How It Works

1. **Input Processing**: The tool extracts the user's original message from conversation history
2. **API Call**: Sends the exact user query to OpenAI's responses API
3. **Research Execution**: OpenAI's o3-deep-research model performs comprehensive investigation
4. **Result Processing**: Extracts research results from the complex response structure
5. **Output**: Returns the research findings directly to the conversation

### Example Usage

```
User: "Research the latest developments in quantum computing"

Tool Response: [Comprehensive research results from OpenAI's deep research model]
```

## 🔍 Technical Details

### API Endpoint

- **Endpoint**: POST /v1/responses
- **Model**: o3-deep-research
- **Required Tools**: web_search_preview

### Request Payload

```json
{
    "model": "o3-deep-research",
    "input": "User's exact query",
    "tools": [
        {
            "type": "web_search_preview"
        }
    ]
}
```

### Response Structure

The tool parses the complex response structure:

```json
{
    "output": [
        {
            "type": "message",
            "content": [
                {
                    "type": "output_text",
                    "text": "Research results content..."
                }
            ]
        }
    ]
}
```

## ⚡ Performance

- **Timeout**: Configurable up to 30 minutes for deep research operations
- **Retry Logic**: Exponential backoff for failed requests
- **Progress Updates**: Real-time status updates during long operations
- **Error Handling**: Graceful handling of API errors and timeouts

## 🔒 Security

- **API Key Management**: Secure storage in tool valves
- **Input Validation**: Proper validation of configuration parameters
- **Error Messages**: User-friendly error messages without exposing sensitive data
- **Timeout Protection**: Prevents hanging requests

## 🛠️ Error Handling

The tool includes comprehensive error handling:

- **API Key Missing**: Clear error message with configuration instructions
- **Network Timeouts**: Retry logic with exponential backoff
- **API Errors**: Different handling for client (4xx) vs server (5xx) errors
- **Invalid Input**: Validation of configuration parameters
- **Response Parsing**: Fallback handling for unexpected response formats

## 📊 Citation Behavior

- **citation=False** (default): Tool output is directly injected into conversation
- **citation=True**: Tool output is treated as a citation/reference

This controls whether the model sees the exact tool output or just a reference to it.

## 🔄 Retry Logic

The tool implements robust retry logic:

- **Maximum Retries**: Configurable via valves (default: 3)
- **Exponential Backoff**: 2^attempt seconds delay between retries
- **Smart Retry**: No retry on client errors (4xx), retry on server errors (5xx)
- **Progress Updates**: Status updates during retry attempts

## 🎯 Input Handling

**CRITICAL**: The tool uses the user's original message exactly as provided:

- Extracts the last user message from conversation history
- Uses the original message, not the model's reformulated input
- Passes the exact user query to the API without modifications
- Preserves the user's original language and structure

## 📝 Requirements

- **Python Packages**: openai==1.0.0, aiohttp==3.9.0, pydantic>=1.8.0
- **OpenAI API Access**: Valid API key with access to o3-deep-research model
- **OpenWebUI**: Compatible OpenWebUI installation

## 🚨 Limitations

- **API Access**: Requires OpenAI API access to o3-deep-research model
- **Response Time**: Deep research can take up to 20 minutes
- **API Costs**: Uses OpenAI's responses API which may have different pricing
- **Model Availability**: Dependent on OpenAI's model availability

## 🔧 Troubleshooting

### Common Issues

1. **"Model does not exist"**: Ensure you have access to o3-deep-research model
2. **"API key required"**: Configure your OpenAI API key in tool settings
3. **"Request timed out"**: Increase timeout value for long research operations
4. **"API request failed"**: Check your API key and network connection

### Debug Mode

Enable debug mode in the valves to get detailed logging information.

## 📚 Related Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenWebUI Documentation](https://docs.openwebui.com/)
- [o3-deep-research Model](https://platform.openai.com/docs/models/o3-deep-research)

## 🤝 Contributing

This tool was created as a workaround to access OpenAI's o3-deep-research model through OpenWebUI. Contributions and improvements are welcome!

## 📄 License

MIT License - see the tool metadata for details.

---

**Author**: Brian Zelun Jin  
**Version**: 1.0.0  
**Last Updated**: 2024 