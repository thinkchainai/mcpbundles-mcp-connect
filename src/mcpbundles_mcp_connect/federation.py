"""Federation completion client for MCP Connect Auth."""

from __future__ import annotations

from typing import Any

import httpx

from mcpbundles_mcp_connect.public_config import (
    DEFAULT_PUBLIC_CONFIG_BASE_URL,
    DEFAULT_HTTP_TIMEOUT,
    tenant_base_url,
)
from mcpbundles_mcp_connect.types import FederationCompleteResult


class FederationCompleteError(RuntimeError):
    """Raised when federation completion fails."""

    def __init__(
        self,
        *,
        listing_slug: str,
        status_code: int,
        detail: str,
    ) -> None:
        self.listing_slug = listing_slug
        self.status_code = status_code
        self.detail = detail
        super().__init__(
            f"Federation complete failed for listing '{listing_slug}' "
            f"(HTTP {status_code}): {detail}"
        )


def federation_complete_url(public_config_base_url: str, listing_slug: str) -> str:
    return f"{tenant_base_url(public_config_base_url, listing_slug)}/v1/federation/complete"


async def complete_federation(
    *,
    listing_slug: str,
    federation_secret: str,
    state: str,
    subject: str,
    organization_id: str | None = None,
    email: str | None = None,
    api_base_url: str = DEFAULT_PUBLIC_CONFIG_BASE_URL,
    timeout: float = DEFAULT_HTTP_TIMEOUT,
    client: httpx.AsyncClient | None = None,
) -> FederationCompleteResult:
    """Complete OAuth federation after your sign-in flow."""
    if not federation_secret:
        raise ValueError("federation_secret is required")
    if not state:
        raise ValueError("state is required")
    if not subject:
        raise ValueError("subject is required")

    url = federation_complete_url(api_base_url, listing_slug)
    body: dict[str, Any] = {"state": state, "subject": subject}
    if organization_id is not None:
        body["organization_id"] = organization_id
    if email is not None:
        body["email"] = email

    headers = {"Authorization": f"Bearer {federation_secret}"}
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=timeout)
    try:
        response = await http.post(url, json=body, headers=headers)
        if response.status_code >= 400:
            detail = response.text
            try:
                payload = response.json()
                if isinstance(payload, dict):
                    detail = str(
                        payload.get("detail")
                        or payload.get("error_description")
                        or payload.get("error")
                        or detail
                    )
            except ValueError:
                pass
            raise FederationCompleteError(
                listing_slug=listing_slug,
                status_code=response.status_code,
                detail=detail,
            )
        payload = response.json()
        if not isinstance(payload, dict):
            raise FederationCompleteError(
                listing_slug=listing_slug,
                status_code=response.status_code,
                detail="response was not a JSON object",
            )
        return payload  # type: ignore[return-value]
    except httpx.HTTPError as exc:
        raise FederationCompleteError(
            listing_slug=listing_slug,
            status_code=0,
            detail=str(exc),
        ) from exc
    finally:
        if owns_client:
            await http.aclose()
