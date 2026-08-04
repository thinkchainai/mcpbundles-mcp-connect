"""Shared sample payloads for unit tests (not packaged for PyPI)."""

from __future__ import annotations

from mcpbundles_mcp_connect.types import PublicConfig

SAMPLE_PUBLIC_CONFIG: PublicConfig = {
    "issuer": "https://api.example.com/connect-auth/tenants/demo",
    "scopes": ["mcp:tools"],
    "origin_resource": "https://mcp.example.com/mcp",
    "bundle_proxy_resource": "https://mcp.mcpbundles.com/bundle/demo",
}

SAMPLE_PUBLIC_CONFIG_WITH_TELEMETRY: PublicConfig = {
    **SAMPLE_PUBLIC_CONFIG,
    "telemetry_ingest_url": (
        "https://api.example.com/connect-auth/tenants/demo/v1/telemetry/handshake"
    ),
}

SAMPLE_OAUTH_METADATA = {
    "issuer": "https://api.example.com/connect-auth/tenants/demo",
    "authorization_endpoint": "https://www.example.com/connect-auth/demo/authorize",
    "token_endpoint": "https://api.example.com/connect-auth/tenants/demo/o/token",
    "registration_endpoint": "https://api.example.com/connect-auth/tenants/demo/o/register",
}
