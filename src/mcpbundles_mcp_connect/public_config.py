"""Fetch tenant public-config from MCPBundles Connect Auth."""

from __future__ import annotations

from collections.abc import Callable

import httpx

from mcpbundles_mcp_connect.types import PublicConfig

INTEGRATION_DOC_URL = "https://www.mcpbundles.com/docs/integrations/mcp-connect-auth"
DEFAULT_PUBLIC_CONFIG_BASE_URL = "https://api.mcpbundles.com"
DEFAULT_HTTP_TIMEOUT = 10.0


def tenant_base_url(public_config_base_url: str, listing_slug: str) -> str:
    base = public_config_base_url.rstrip("/")
    return f"{base}/connect-auth/tenants/{listing_slug}"


def public_config_url(public_config_base_url: str, listing_slug: str) -> str:
    return f"{tenant_base_url(public_config_base_url, listing_slug)}/public-config"


def jwks_url(public_config_base_url: str, listing_slug: str) -> str:
    return (
        f"{tenant_base_url(public_config_base_url, listing_slug)}/.well-known/jwks.json"
    )


def oauth_authorization_server_metadata_url(
    public_config_base_url: str,
    listing_slug: str,
) -> str:
    return (
        f"{tenant_base_url(public_config_base_url, listing_slug)}"
        "/.well-known/oauth-authorization-server"
    )


class PublicConfigFetchError(RuntimeError):
    """Raised when tenant public-config cannot be loaded."""

    def __init__(
        self,
        *,
        listing_slug: str,
        url: str,
        reason: str,
    ) -> None:
        self.listing_slug = listing_slug
        self.url = url
        self.reason = reason
        super().__init__(
            "Failed to load MCP Connect Auth public-config for listing "
            f"'{listing_slug}' from {url}: {reason}. "
            f"See {INTEGRATION_DOC_URL} for setup instructions."
        )


def fetch_public_config(
    listing_slug: str,
    *,
    public_config_base_url: str = DEFAULT_PUBLIC_CONFIG_BASE_URL,
    timeout: float = DEFAULT_HTTP_TIMEOUT,
    client: httpx.Client | None = None,
) -> PublicConfig:
    """Load tenant public-config synchronously."""
    url = public_config_url(public_config_base_url, listing_slug)
    owns_client = client is None
    http = client or httpx.Client(timeout=timeout)
    try:
        response = http.get(url)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise PublicConfigFetchError(
                listing_slug=listing_slug,
                url=url,
                reason="response was not a JSON object",
            )
        return _validate_public_config(payload, listing_slug=listing_slug, url=url)
    except httpx.HTTPError as exc:
        raise PublicConfigFetchError(
            listing_slug=listing_slug,
            url=url,
            reason=str(exc),
        ) from exc
    finally:
        if owns_client:
            http.close()


def _validate_public_config(
    payload: dict[str, object],
    *,
    listing_slug: str,
    url: str,
) -> PublicConfig:
    issuer = payload.get("issuer")
    origin_resource = payload.get("origin_resource")
    bundle_proxy_resource = payload.get("bundle_proxy_resource")
    missing: list[str] = []
    if not isinstance(issuer, str) or not issuer:
        missing.append("issuer")
    if not isinstance(origin_resource, str) or not origin_resource:
        missing.append("origin_resource")
    if not isinstance(bundle_proxy_resource, str) or not bundle_proxy_resource:
        missing.append("bundle_proxy_resource")
    if missing:
        raise PublicConfigFetchError(
            listing_slug=listing_slug,
            url=url,
            reason=f"missing required fields: {', '.join(missing)}",
        )

    config: PublicConfig = {
        "issuer": issuer,
        "origin_resource": origin_resource,
        "bundle_proxy_resource": bundle_proxy_resource,
    }
    scopes_supported = payload.get("scopes_supported")
    if isinstance(scopes_supported, list):
        config["scopes_supported"] = [
            scope for scope in scopes_supported if isinstance(scope, str)
        ]
    telemetry_ingest_url = payload.get("telemetry_ingest_url")
    if isinstance(telemetry_ingest_url, str) and telemetry_ingest_url:
        config["telemetry_ingest_url"] = telemetry_ingest_url
    return config


PublicConfigFetcher = Callable[..., PublicConfig]
