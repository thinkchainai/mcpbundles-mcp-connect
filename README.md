# mcpbundles-mcp-connect

Python client library for [MCP Connect Auth](https://www.mcpbundles.com/docs/integrations/mcp-connect-auth) on MCPBundles.

- `connect_auth_callback_identity()` — canonical `get-user-info` JSON from a verified FastMCP token
- `McpbundlesConnectProvider` — FastMCP auth (interim package export until upstream FastMCP merge)
- `mcpbundles_fastmcp()` — one-line FastMCP setup (auth + optional origin handshake telemetry)
- `complete_federation()` — finish OAuth federation after your sign-in flow
- `McpbundlesHandshakeMiddleware` — origin initialize cohort ingest when telemetry is enabled

## Identity in tool callbacks

Connect Auth separates **who signed in** (`sub`, optional `organization_id`, `email`, `roles`) from **which MCP client** is calling (`client_id`). Pass `email` and `roles` in federation `complete` to mint them on access tokens.

In FastMCP tools, use `connect_auth_callback_identity(get_access_token())` for the same JSON shape as the mcp-use `get-user-info` example. See [Tool callback identity](https://www.mcpbundles.com/docs/integrations/mcp-connect-auth#tool-callback-identity).

## Path B — bundle URL only

Publish with MCP Connect Auth, set your federation sign-in URL, and have clients connect via `https://mcp.mcpbundles.com/bundle/{slug}`. No pip install required on your MCP server.

## Path A — vendor origin (FastMCP)

```python
from mcpbundles_mcp_connect import connect_auth_callback_identity, mcpbundles_fastmcp
from fastmcp.server.dependencies import get_access_token

mcp = mcpbundles_fastmcp(
    "My App",
    listing_slug="my-listing",
    base_url="https://mcp.example.com",
)

@mcp.tool
def get_user_info() -> dict:
    token = get_access_token()
    if token is None:
        return {"error": "Not authenticated"}
    return connect_auth_callback_identity(token)
```

After sign-in on your web app, complete federation server-side:

```python
from mcpbundles_mcp_connect import complete_federation

await complete_federation(
    listing_slug="my-listing",
    federation_secret=os.environ["MCPBUNDLES_FEDERATION_SECRET"],
    state=state_from_redirect,
    subject=user_id,
    organization_id=organization_id,
    email=user_email,
    roles=user_roles,
)
```

Full setup guide: https://www.mcpbundles.com/docs/integrations/mcp-connect-auth

```bash
pip install mcpbundles-mcp-connect
```
