"""Tests for McpbundlesConnectProvider."""

from __future__ import annotations

import httpx
import pytest

from mcpbundles_mcp_connect.fastmcp.jwt_verifier import McpbundlesJWTVerifier
from mcpbundles_mcp_connect.fastmcp.provider import McpbundlesConnectProvider
from mcpbundles_mcp_connect.middleware import McpbundlesHandshakeMiddleware
from .sample_data import (
    SAMPLE_OAUTH_METADATA,
    SAMPLE_PUBLIC_CONFIG,
    SAMPLE_PUBLIC_CONFIG_WITH_TELEMETRY,
)


def _provider(**kwargs) -> McpbundlesConnectProvider:
    defaults = {
        "listing_slug": "demo",
        "base_url": "https://mcp.example.com",
        "public_config": SAMPLE_PUBLIC_CONFIG,
    }
    defaults.update(kwargs)
    return McpbundlesConnectProvider(**defaults)


def test_provider_configures_jwt_verifier() -> None:
    provider = _provider()

    assert isinstance(provider.token_verifier, McpbundlesJWTVerifier)
    assert provider.token_verifier.issuer == SAMPLE_PUBLIC_CONFIG["issuer"]
    assert provider.token_verifier.algorithm == "ES256"
    assert provider.token_verifier.audience == [
        SAMPLE_PUBLIC_CONFIG["origin_resource"],
        SAMPLE_PUBLIC_CONFIG["bundle_proxy_resource"],
    ]
    assert provider.token_verifier.jwks_uri.endswith(
        "/connect-auth/tenants/demo/.well-known/jwks.json"
    )


def test_provider_authorization_servers() -> None:
    provider = _provider()

    assert len(provider.authorization_servers) == 1
    assert str(provider.authorization_servers[0]).endswith(
        "/connect-auth/tenants/demo"
    )


def test_default_middleware_without_telemetry() -> None:
    provider = _provider()
    assert provider.default_middleware() == []


def test_default_middleware_with_telemetry() -> None:
    provider = _provider(public_config=SAMPLE_PUBLIC_CONFIG_WITH_TELEMETRY)
    middleware = provider.default_middleware()

    assert len(middleware) == 1
    assert isinstance(middleware[0], McpbundlesHandshakeMiddleware)
    assert middleware[0].ingest_url == SAMPLE_PUBLIC_CONFIG_WITH_TELEMETRY[
        "telemetry_ingest_url"
    ]


@pytest.mark.asyncio
async def test_metadata_route_forwards_tenant_response() -> None:
    provider = _provider()
    routes = provider.get_routes(mcp_path="/mcp")
    metadata_route = next(
        route
        for route in routes
        if getattr(route, "path", None) == "/.well-known/oauth-authorization-server"
    )

    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json=SAMPLE_OAUTH_METADATA)

    original_async_client = httpx.AsyncClient

    class PatchedAsyncClient(original_async_client):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(handler)
            super().__init__(*args, **kwargs)

    httpx.AsyncClient = PatchedAsyncClient  # type: ignore[misc, assignment]
    try:
        response = await metadata_route.endpoint(None)  # type: ignore[arg-type]
    finally:
        httpx.AsyncClient = original_async_client

    assert response.status_code == 200
    assert response.body is not None
    assert captured["url"].endswith(
        "/connect-auth/tenants/demo/.well-known/oauth-authorization-server"
    )
