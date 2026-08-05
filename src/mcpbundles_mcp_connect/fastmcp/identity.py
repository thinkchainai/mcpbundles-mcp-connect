"""Map verified Connect Auth access tokens to the canonical callback shape."""

from __future__ import annotations

from typing import Any

from fastmcp.server.auth import AccessToken


def connect_auth_callback_identity(access_token: AccessToken) -> dict[str, Any]:
    """Build the canonical Connect Auth tool callback shape from a verified token."""
    claims = access_token.claims
    organization_id = claims.get("organization_id")
    email = claims.get("email")
    roles_raw = claims.get("roles")
    roles: list[str] = []
    if isinstance(roles_raw, list):
        roles = [role for role in roles_raw if isinstance(role, str)]

    audience = claims.get("aud")
    resource: str | None = None
    if isinstance(audience, str):
        resource = audience
    elif isinstance(audience, list) and audience:
        first = audience[0]
        if isinstance(first, str):
            resource = first

    subject = access_token.subject
    if not subject and isinstance(claims.get("sub"), str):
        subject = claims["sub"]

    return {
        "user": {
            "id": subject or "",
            "organizationId": organization_id if isinstance(organization_id, str) else None,
            "email": email if isinstance(email, str) and email else None,
            "roles": roles,
        },
        "auth": {
            "clientId": access_token.client_id,
            "scopes": list(access_token.scopes or []),
            "expiresAt": access_token.expires_at,
            "resource": resource,
        },
    }
