"""MCP Connect Auth client library for Python."""

from mcpbundles_mcp_connect.factory import mcpbundles_fastmcp
from mcpbundles_mcp_connect.fastmcp import McpbundlesConnectProvider
from mcpbundles_mcp_connect.federation import (
    FederationCompleteError,
    complete_federation,
)
from mcpbundles_mcp_connect.middleware import McpbundlesHandshakeMiddleware
from mcpbundles_mcp_connect.public_config import (
    INTEGRATION_DOC_URL,
    PublicConfigFetchError,
    fetch_public_config,
)

__version__ = "0.1.0"

__all__ = [
    "INTEGRATION_DOC_URL",
    "FederationCompleteError",
    "McpbundlesConnectProvider",
    "McpbundlesHandshakeMiddleware",
    "PublicConfigFetchError",
    "complete_federation",
    "fetch_public_config",
    "mcpbundles_fastmcp",
]
