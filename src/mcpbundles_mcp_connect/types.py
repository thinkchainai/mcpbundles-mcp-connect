"""Shared types for MCP Connect Auth client library."""

from __future__ import annotations

from typing import TypedDict


class PublicConfig(TypedDict, total=False):
    """Tenant public-config response from MCPBundles Connect Auth."""

    issuer: str
    scopes: list[str]
    origin_resource: str
    bundle_proxy_resource: str
    telemetry_ingest_url: str


class FederationCompleteResult(TypedDict, total=False):
    """Successful federation complete response."""

    status: str
    subject: str
    organization_id: str | None
