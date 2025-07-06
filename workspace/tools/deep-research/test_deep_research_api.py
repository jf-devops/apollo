#!/usr/bin/env python3
"""
Test script for Deep Research Tool API calls
Allows testing the OpenAI o3-deep-research API outside of OpenWebUI
"""

import asyncio
import aiohttp
import json
from typing import Optional
from datetime import datetime

class DeepResearchTester:
    def __init__(self):
        self.api_key: Optional[str] = None
        self.base_url: str = "https://api.openai.com/v1"
        self.model_name: str = "o3-deep-research"
        self.timeout: int = 1800  # 30 minutes
        self.max_retries: int = 3
        
    def get_api_key(self) -> str:
        """Get API key from user input"""
        print("\n" + "="*60)
        print("🔑 OPENAI API KEY SETUP")
        print("="*60)
        print("You need an OpenAI API key to test the deep research tool.")
        print("Get one from: https://platform.openai.com/api-keys")
        print()
        
        while True:
            api_key = input("Enter your OpenAI API key: ").strip()
            if api_key:
                if api_key.startswith("sk-"):
                    self.api_key = api_key
                    print("✅ API key set successfully!")
                    return api_key
                else:
                    print("❌ Invalid API key format. Should start with 'sk-'")
            else:
                print("❌ API key cannot be empty")
    
    def get_test_query(self) -> str:
        """Get test query from user input"""
        print("\n" + "="*60)
        print("🔍 DEEP RESEARCH QUERY")
        print("="*60)
        print("Enter a query to test the deep research functionality.")
        print("Examples:")
        print("- 'What are the latest developments in quantum computing?'")
        print("- 'Research the impact of AI on healthcare in 2024'")
        print("- 'Compare different approaches to renewable energy storage'")
        print()
        
        while True:
            query = input("Enter your query: ").strip()
            if query:
                return query
            else:
                print("❌ Query cannot be empty")
    
    async def test_api_call(self, query: str) -> dict:
        """Test the actual API call to OpenAI"""
        print(f"\n🚀 Testing API call...")
        print(f"Query: {query}")
        print(f"Model: {self.model_name}")
        print(f"Timeout: {self.timeout} seconds")
        print(f"Max Retries: {self.max_retries}")
        print()
        
        # Prepare the request payload for responses API
        payload = {
            "model": self.model_name,
            "input": query,
            "tools": [
                {
                    "type": "web_search_preview"
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                print(f"📡 Sending request to OpenAI responses API (attempt {attempt + 1}/{self.max_retries + 1})...")
                start_time = datetime.now()
                
                # Make the API request
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.base_url}/responses",
                        json=payload,
                        headers=headers
                    ) as response:
                        end_time = datetime.now()
                        duration = (end_time - start_time).total_seconds()
                        
                        print(f"⏱️  Request completed in {duration:.2f} seconds")
                        print(f"📊 Response status: {response.status}")
                        
                        if response.status == 200:
                            data = await response.json()
                            print("✅ API call successful!")
                            
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
                            
                            return {
                                "success": True,
                                "status_code": response.status,
                                "duration": duration,
                                "response": research_results,
                                "full_response": data
                            }
                        else:
                            error_text = await response.text()
                            last_error = f"API request failed with status {response.status}: {error_text}"
                            print(f"❌ API call failed!")
                            print(f"Error: {error_text}")
                            
                            # Don't retry on client errors (4xx)
                            if 400 <= response.status < 500:
                                return {
                                    "success": False,
                                    "status_code": response.status,
                                    "duration": duration,
                                    "error": last_error
                                }
                            
                            # Retry on server errors (5xx) or network issues
                            if attempt < self.max_retries:
                                print(f"🔄 Retrying... (attempt {attempt + 1}/{self.max_retries + 1})")
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            else:
                                return {
                                    "success": False,
                                    "status_code": response.status,
                                    "duration": duration,
                                    "error": last_error
                                }
                                
            except asyncio.TimeoutError:
                last_error = f"Request timed out after {self.timeout} seconds"
                print(f"❌ Request timed out!")
                
                if attempt < self.max_retries:
                    print(f"🔄 Retrying... (attempt {attempt + 1}/{self.max_retries + 1})")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return {
                        "success": False,
                        "error": last_error
                    }
            except Exception as e:
                last_error = f"Error during API call: {str(e)}"
                print(f"❌ Error during API call: {str(e)}")
                
                if attempt < self.max_retries:
                    print(f"🔄 Retrying... (attempt {attempt + 1}/{self.max_retries + 1})")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return {
                        "success": False,
                        "error": last_error
                    }
        
        # If we get here, all retries failed
        return {
            "success": False,
            "error": last_error or "All retry attempts failed"
        }
    
    def display_results(self, results: dict):
        """Display the test results"""
        print("\n" + "="*60)
        print("📋 TEST RESULTS")
        print("="*60)
        
        if results["success"]:
            print("✅ Test PASSED!")
            print(f"⏱️  Duration: {results.get('duration', 'N/A')} seconds")
            print(f"📊 Status Code: {results.get('status_code', 'N/A')}")
            print()
            print("📄 RESPONSE CONTENT:")
            print("-" * 40)
            print(results["response"])
            print("-" * 40)
            print("Note: This is the raw output from the o3-deep-research API")
            print("The API was called with the exact user input provided")
            
            # Optionally show full response structure
            show_full = input("\nShow full API response structure? (y/n): ").lower().strip()
            if show_full == 'y':
                print("\n🔍 FULL API RESPONSE:")
                print(json.dumps(results["full_response"], indent=2))
        else:
            print("❌ Test FAILED!")
            print(f"Error: {results.get('error', 'Unknown error')}")
    
    async def run_test(self):
        """Run the complete test"""
        print("🧪 DEEP RESEARCH TOOL API TESTER")
        print("This script tests the OpenAI o3-deep-research API calls")
        print("outside of the OpenWebUI environment.")
        
        # Get API key
        self.get_api_key()
        
        # Get test query
        query = self.get_test_query()
        
        # Run the test
        results = await self.test_api_call(query)
        
        # Display results
        self.display_results(results)
        
        # Ask if user wants to test another query
        while True:
            another = input("\nTest another query? (y/n): ").lower().strip()
            if another == 'y':
                query = self.get_test_query()
                results = await self.test_api_call(query)
                self.display_results(results)
            elif another == 'n':
                break
            else:
                print("Please enter 'y' or 'n'")
        
        print("\n👋 Test completed! Thanks for testing the Deep Research Tool.")

async def main():
    """Main function"""
    tester = DeepResearchTester()
    await tester.run_test()

if __name__ == "__main__":
    print("Starting Deep Research Tool API Tester...")
    asyncio.run(main()) 