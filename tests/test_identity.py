"""Tests for connect_auth_callback_identity."""

from __future__ import annotations

from fastmcp.server.auth import AccessToken

from mcpbundles_mcp_connect.fastmcp.identity import connect_auth_callback_identity


def test_connect_auth_callback_identity_shape() -> None:
    token = AccessToken(
        token="jwt",
        client_id="mcp-client-1",
        scopes=["read", "write"],
        expires_at=1_700_000_999,
        subject="user-1",
        claims={
            "sub": "user-1",
            "organization_id": "org-1",
            "email": "builder@example.test",
            "roles": ["admin"],
            "aud": "https://mcp.example.com/mcp",
        },
    )

    assert connect_auth_callback_identity(token) == {
        "user": {
            "id": "user-1",
            "organizationId": "org-1",
            "email": "builder@example.test",
            "roles": ["admin"],
        },
        "auth": {
            "clientId": "mcp-client-1",
            "scopes": ["read", "write"],
            "expiresAt": 1_700_000_999,
            "resource": "https://mcp.example.com/mcp",
        },
    }
