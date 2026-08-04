"""FastMCP factory helper for MCP Connect Auth."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from pydantic import AnyHttpUrl

from mcpbundles_mcp_connect.fastmcp.provider import McpbundlesConnectProvider
from mcpbundles_mcp_connect.public_config import DEFAULT_PUBLIC_CONFIG_BASE_URL
from mcpbundles_mcp_connect.types import PublicConfig


def mcpbundles_fastmcp(
    name: str,
    *,
    listing_slug: str,
    base_url: AnyHttpUrl | str,
    required_scopes: list[str] | None = None,
    scopes_supported: list[str] | None = None,
    resource_name: str | None = None,
    resource_documentation: AnyHttpUrl | None = None,
    public_config_base_url: str = DEFAULT_PUBLIC_CONFIG_BASE_URL,
    public_config: PublicConfig | None = None,
    **fastmcp_kwargs: Any,
) -> FastMCP:
    """Create a FastMCP server with MCP Connect Auth and optional telemetry."""
    provider = McpbundlesConnectProvider(
        listing_slug=listing_slug,
        base_url=base_url,
        required_scopes=required_scopes,
        scopes_supported=scopes_supported,
        resource_name=resource_name,
        resource_documentation=resource_documentation,
        public_config_base_url=public_config_base_url,
        public_config=public_config,
    )
    middleware = provider.default_middleware()
    return FastMCP(
        name,
        auth=provider,
        middleware=middleware or None,
        **fastmcp_kwargs,
    )
