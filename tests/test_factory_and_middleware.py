"""Tests for handshake middleware and factory."""

from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from fastmcp import FastMCP

from mcpbundles_mcp_connect.factory import mcpbundles_fastmcp
from mcpbundles_mcp_connect.middleware import McpbundlesHandshakeMiddleware
from tests.conftest import SAMPLE_PUBLIC_CONFIG_WITH_TELEMETRY


class DummyInitializeParams(SimpleNamespace):
    pass


class DummyInitializeRequest(SimpleNamespace):
    pass


@pytest.mark.asyncio
async def test_handshake_middleware_posts_ingest_without_blocking() -> None:
    posted: dict[str, Any] = {}
    done = asyncio.Event()

    def handler(request: httpx.Request) -> httpx.Response:
        posted["url"] = str(request.url)
        posted["json"] = request.content.decode("utf-8")
        done.set()
        return httpx.Response(204)

    middleware = McpbundlesHandshakeMiddleware(
        ingest_url=SAMPLE_PUBLIC_CONFIG_WITH_TELEMETRY["telemetry_ingest_url"],
        listing_slug="demo",
    )

    async def call_next(context):
        return SimpleNamespace(protocol_version="2025-03-26")

    request = DummyInitializeRequest(
        params=DummyInitializeParams(
            client_info=SimpleNamespace(name="Cursor", version="1.0.0"),
            protocol_version="2025-03-26",
            capabilities={"tools": {}},
        )
    )
    context = SimpleNamespace(message=request)

    class PatchedAsyncClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(handler)
            super().__init__(*args, **kwargs)

    with patch(
        "mcpbundles_mcp_connect.middleware.httpx.AsyncClient",
        PatchedAsyncClient,
    ):
        result = await middleware.on_initialize(context, call_next)  # type: ignore[arg-type]
        assert result.protocol_version == "2025-03-26"
        await asyncio.wait_for(done.wait(), timeout=1.0)

    assert posted["url"] == SAMPLE_PUBLIC_CONFIG_WITH_TELEMETRY["telemetry_ingest_url"]
    assert "Cursor" in posted["json"]


def test_mcpbundles_fastmcp_registers_auth_and_middleware() -> None:
    mcp = mcpbundles_fastmcp(
        "Demo",
        listing_slug="demo",
        base_url="https://mcp.example.com",
        public_config=SAMPLE_PUBLIC_CONFIG_WITH_TELEMETRY,
    )

    assert isinstance(mcp, FastMCP)
    assert mcp.auth is not None
    assert mcp.auth.listing_slug == "demo"
    handshake_middleware = [
        item for item in mcp.middleware if isinstance(item, McpbundlesHandshakeMiddleware)
    ]
    assert len(handshake_middleware) == 1
