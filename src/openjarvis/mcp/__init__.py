"""MCP (Model Context Protocol) layer for Silas."""

from silas.mcp.client import MCPClient
from silas.mcp.protocol import MCPError, MCPNotification, MCPRequest, MCPResponse
from silas.mcp.server import MCPServer
from silas.mcp.transport import (
    InProcessTransport,
    MCPTransport,
    SSETransport,
    StdioTransport,
    StreamableHTTPTransport,
)

__all__ = [
    "MCPClient",
    "MCPError",
    "MCPNotification",
    "MCPRequest",
    "MCPResponse",
    "MCPServer",
    "MCPTransport",
    "InProcessTransport",
    "SSETransport",
    "StdioTransport",
    "StreamableHTTPTransport",
]
