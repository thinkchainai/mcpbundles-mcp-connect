"""Pytest configuration for mcpbundles-mcp-connect."""

from __future__ import annotations

from .sample_data import (  # noqa: F401 — re-export for pytest fixtures
    SAMPLE_OAUTH_METADATA,
    SAMPLE_PUBLIC_CONFIG,
    SAMPLE_PUBLIC_CONFIG_WITH_TELEMETRY,
)
