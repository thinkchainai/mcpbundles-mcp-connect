"""Tests for federation completion client."""

from __future__ import annotations

import json

import httpx
import pytest

from mcpbundles_mcp_connect.federation import (
    FederationCompleteError,
    complete_federation,
    federation_complete_url,
)


@pytest.mark.asyncio
async def test_complete_federation_success() -> None:
    url = federation_complete_url("https://api.example.com", "demo")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == url
        assert request.headers["Authorization"] == "Bearer test-secret"
        payload = json.loads(request.content.decode("utf-8"))
        assert payload["state"] == "state-123"
        assert payload["subject"] == "user-456"
        return httpx.Response(200, json={"status": "ok", "subject": "user-456"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await complete_federation(
            listing_slug="demo",
            federation_secret="test-secret",
            state="state-123",
            subject="user-456",
            api_base_url="https://api.example.com",
            client=client,
        )

    assert result["status"] == "ok"
    assert result["subject"] == "user-456"


@pytest.mark.asyncio
async def test_complete_federation_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={"error": "invalid_secret", "error_description": "bad secret"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(FederationCompleteError) as exc_info:
            await complete_federation(
                listing_slug="demo",
                federation_secret="bad-secret",
                state="state-123",
                subject="user-456",
                api_base_url="https://api.example.com",
                client=client,
            )

    assert exc_info.value.status_code == 401
    assert "bad secret" in exc_info.value.detail


@pytest.mark.asyncio
async def test_complete_federation_requires_secret() -> None:
    with pytest.raises(ValueError, match="federation_secret"):
        await complete_federation(
            listing_slug="demo",
            federation_secret="",
            state="state-123",
            subject="user-456",
        )
