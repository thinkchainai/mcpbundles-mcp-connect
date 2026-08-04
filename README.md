# mcpbundles-mcp-connect

Python client library for [MCP Connect Auth](https://www.mcpbundles.com/docs/integrations/mcp-connect-auth) on MCPBundles.

- `McpbundlesConnectProvider` — FastMCP auth (interim re-export until upstream FastMCP merge)
- `mcpbundles_fastmcp()` — one-line FastMCP setup (auth + optional origin handshake telemetry)
- `complete_federation()` — finish OAuth federation after your sign-in flow
- ASGI middleware for non-FastMCP servers

**Status:** Scaffold only — implementation tracked in the main MCPBundles monorepo (`product/mcp-connect-auth/coding-plan.md`).

```bash
pip install mcpbundles-mcp-connect  # not published yet
```
