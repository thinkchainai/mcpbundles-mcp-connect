# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-08-05

### Added

- `connect_auth_callback_identity()` — canonical `get-user-info` JSON from a verified FastMCP access token (matches mcp-use example and integration doc § Tool callback identity).
- `roles` parameter on `complete_federation()` for pass-through federation profile claims.

### Fixed

- Release tags now bump `pyproject.toml` version so PyPI publishes distinct artifacts (0.1.1 tag had been blocked on duplicate 0.1.0).

## [0.1.0] - 2026-08-04

### Added

- Initial PyPI release of the MCP Connect Auth Python client.
- `McpbundlesConnectProvider` for FastMCP resource-server auth (JWT verification, OAuth metadata proxy route).
- `mcpbundles_fastmcp()` factory wiring auth and optional origin handshake telemetry middleware.
- `complete_federation()` client for finishing OAuth federation after your sign-in flow.
- `fetch_public_config()` helper for loading tenant public-config from MCPBundles.
- `McpbundlesHandshakeMiddleware` for fire-and-forget initialize cohort ingest when telemetry is enabled.
- `py.typed` marker for PEP 561 typing support.
- GitHub Actions CI (pytest, wheel build, import smoke test) and tag-based PyPI release workflow.

### Fixed

- Wheel packaging now includes the `mcpbundles_mcp_connect.fastmcp` subpackage.
- Public-config parsing reads `scopes_supported` to match the MCPBundles API and npm client.
- Handshake telemetry truncates `client_name` / `client_version` to 200 characters and sends `protocol_negotiated`.

[0.1.2]: https://github.com/thinkchainai/mcpbundles-mcp-connect/releases/tag/v0.1.2
[0.1.0]: https://github.com/thinkchainai/mcpbundles-mcp-connect/releases/tag/v0.1.0
