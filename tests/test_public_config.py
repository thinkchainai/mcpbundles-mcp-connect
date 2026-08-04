"""Tests for public-config fetching."""

from __future__ import annotations

import httpx
import pytest

from mcpbundles_mcp_connect.public_config import (
    PublicConfigFetchError,
    fetch_public_config,
    public_config_url,
)
from .sample_data import SAMPLE_PUBLIC_CONFIG


def test_fetch_public_config_success() -> None:
    url = public_config_url("https://api.example.com", "demo")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == url
        return httpx.Response(200, json=SAMPLE_PUBLIC_CONFIG)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        config = fetch_public_config(
            "demo",
            public_config_base_url="https://api.example.com",
            client=client,
        )

    assert config["issuer"] == SAMPLE_PUBLIC_CONFIG["issuer"]
    assert config["origin_resource"] == SAMPLE_PUBLIC_CONFIG["origin_resource"]


def test_fetch_public_config_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "not found"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(PublicConfigFetchError) as exc_info:
            fetch_public_config(
                "missing",
                public_config_base_url="https://api.example.com",
                client=client,
            )

    assert "missing" in str(exc_info.value)
    assert "public-config" in exc_info.value.url


def test_fetch_public_config_missing_required_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"issuer": "https://issuer.example.com"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(PublicConfigFetchError) as exc_info:
            fetch_public_config(
                "demo",
                public_config_base_url="https://api.example.com",
                client=client,
            )

    assert "origin_resource" in str(exc_info.value)
