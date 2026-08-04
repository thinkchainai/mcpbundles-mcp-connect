# mcpbundles-mcp-connect — Agent Context

Public PyPI package for MCP Connect Auth on MCPBundles. Submodule of [mcp_bundles](https://github.com/thinkchainai/mcp) at `public_github_repos/mcpbundles-mcp-connect`.

**Execution checklist:** `product/mcp-connect-auth/coding-plan.md` § P1b in the parent monorepo.

## Scope

- `McpbundlesConnectProvider` (interim re-export from `thinkchainai/fastmcp` fork until PrefectHQ merge)
- `mcpbundles_fastmcp()` factory — auth + optional `McpbundlesHandshakeMiddleware`
- `complete_federation()` HTTP client
- Optional Starlette/ASGI middleware for non-FastMCP servers

## Release

- Tag `vX.Y.Z` → GitHub Actions PyPI publish (add workflow in P1b)
- Parent monorepo bumps submodule pointer after release

## Rules

- No secrets in README or examples; federation secret is server-side only
- Provider imports only **public** `fastmcp` APIs for vendor compatibility
