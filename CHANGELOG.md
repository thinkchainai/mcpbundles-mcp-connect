# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/thinkchainai/mcpbundles-mcp-connect/releases/tag/v0.1.0
