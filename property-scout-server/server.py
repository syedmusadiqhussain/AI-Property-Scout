#!/usr/bin/env python3
import asyncio
import os
import sys
from typing import Any, Sequence

from dotenv import load_dotenv
from mcp import Tool
from mcp.server import Server
from mcp.types import (
    CallToolRequest,
    ErrorCode,
    ListToolsRequest,
    McpError,
    TextContent,
    PromptMessage,
)
import requests

load_dotenv()

SERPER_API_KEY = os.getenv('SERPER_API_KEY')
BROWSERLESS_API_KEY = os.getenv('BROWSERLESS_API_KEY')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

if not SERPER_API_KEY:
    raise ValueError('SERPER_API_KEY environment variable is required')
if not BROWSERLESS_API_KEY:
    raise ValueError('BROWSERLESS_API_KEY environment variable is required')
if not HUGGINGFACE_API_KEY:
    raise ValueError('HUGGINGFACE_API_KEY environment variable is required')

server = Server("property-scout-server")

@server.call_tool()
async def call_tool(request: CallToolRequest) -> Sequence[TextContent]:
    if request.name == "search_properties":
        if not request.arguments or "query" not in request.arguments:
            raise McpError(ErrorCode.INVALID_PARAMS, "Missing query parameter")

        query = request.arguments["query"]

        try:
            response = requests.post(
                'https://google.serper.dev/search',
                json={
                    'q': query,
                    'num': 10,
                },
                headers={
                    'X-API-KEY': SERPER_API_KEY,
                    'Content-Type': 'application/json',
                },
            )
            response.raise_for_status()

            return [TextContent(type="text", text=response.text)]
        except requests.RequestException as e:
            return [TextContent(type="text", text=f"Serper API error: {str(e)}")]

    elif request.name == "extract_property_data":
        if not request.arguments or "url" not in request.arguments:
            raise McpError(ErrorCode.INVALID_PARAMS, "Missing url parameter")

        url = request.arguments["url"]

        try:
            response = requests.post(
                f'https://chrome.browserless.io/content?token={BROWSERLESS_API_KEY}',
                json={
                    'url': url,
                    'waitFor': 2000,
                    'gotoOptions': {'waitUntil': 'networkidle0'},
                },
                headers={
                    'Content-Type': 'application/json',
                },
            )
            response.raise_for_status()

            return [TextContent(type="text", text=response.text)]
        except requests.RequestException as e:
            return [TextContent(type="text", text=f"Browserless API error: {str(e)}")]

    elif request.name == "analyze_properties":
        if not request.arguments or "text" not in request.arguments:
            raise McpError(ErrorCode.INVALID_PARAMS, "Missing text parameter")

        text = request.arguments["text"]

        try:
            response = requests.post(
                'https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english',
                json={
                    'inputs': text,
                },
                headers={
                    'Authorization': f'Bearer {HUGGINGFACE_API_KEY}',
                    'Content-Type': 'application/json',
                },
            )
            response.raise_for_status()

            return [TextContent(type="text", text=response.text)]
        except requests.RequestException as e:
            return [TextContent(type="text", text=f"Hugging Face API error: {str(e)}")]

    else:
        raise McpError(ErrorCode.METHOD_NOT_FOUND, f"Unknown tool: {request.name}")

@server.list_tools()
async def list_tools(request: ListToolsRequest) -> list[Tool]:
    return [
        Tool(
            name="search_properties",
            description="Search for properties using Google search via Serper API",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for properties",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="extract_property_data",
            description="Extract property data from a webpage using Browserless",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the property listing page",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="analyze_properties",
            description="Analyze property data using Hugging Face",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Property data text to analyze",
                    },
                },
                "required": ["text"],
            },
        ),
    ]

async def main():
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
