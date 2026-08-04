# mcpbundles-mcp-connect

Python client library for [MCP Connect Auth](https://www.mcpbundles.com/docs/integrations/mcp-connect-auth) on MCPBundles.

- `McpbundlesConnectProvider` — FastMCP auth (interim package export until upstream FastMCP merge)
- `mcpbundles_fastmcp()` — one-line FastMCP setup (auth + optional origin handshake telemetry)
- `complete_federation()` — finish OAuth federation after your sign-in flow
- `McpbundlesHandshakeMiddleware` — origin initialize cohort ingest when telemetry is enabled

## Path B — bundle URL only

Publish with MCP Connect Auth, set your federation sign-in URL, and have clients connect via `https://mcp.mcpbundles.com/bundle/{slug}`. No pip install required on your MCP server.

## Path A — vendor origin (FastMCP)

```python
from mcpbundles_mcp_connect import mcpbundles_fastmcp

mcp = mcpbundles_fastmcp(
    "My App",
    listing_slug="my-listing",
    base_url="https://mcp.example.com",
)

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

After sign-in on your web app, complete federation server-side:

```python
from mcpbundles_mcp_connect import complete_federation

await complete_federation(
    listing_slug="my-listing",
    federation_secret=os.environ["MCPBUNDLES_FEDERATION_SECRET"],
    state=state_from_redirect,
    subject=user_id,
)
```

Full setup guide: https://www.mcpbundles.com/docs/integrations/mcp-connect-auth

```bash
pip install mcpbundles-mcp-connect
```
