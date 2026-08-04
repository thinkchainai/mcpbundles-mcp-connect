"""MCPBundles Connect Auth provider for FastMCP."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
from pydantic import AnyHttpUrl
from starlette.responses import JSONResponse
from starlette.routing import Route

from fastmcp.server.auth import RemoteAuthProvider, TokenVerifier
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.middleware import Middleware
from fastmcp.utilities.auth import parse_scopes
from fastmcp.utilities.logging import get_logger

from mcpbundles_mcp_connect.middleware import McpbundlesHandshakeMiddleware
from mcpbundles_mcp_connect.public_config import (
    DEFAULT_PUBLIC_CONFIG_BASE_URL,
    INTEGRATION_DOC_URL,
    PublicConfigFetcher,
    fetch_public_config,
    jwks_url,
    oauth_authorization_server_metadata_url,
    tenant_base_url,
)
from mcpbundles_mcp_connect.types import PublicConfig

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = get_logger(__name__)


class McpbundlesConnectProvider(RemoteAuthProvider):
    """MCPBundles Connect Auth resource server provider for FastMCP.

    IMPORTANT SETUP REQUIREMENTS:

    1. Publish your MCP server on MCPBundles with MCP Connect Auth enabled.
    2. Set your federation sign-in URL and save the federation secret on your
       web app (not in this MCP server).
    3. Configure ``MCPBUNDLES_LISTING_SLUG`` and point clients at your public
       MCP origin URL via ``base_url``.

    For detailed setup instructions, see:
    https://www.mcpbundles.com/docs/integrations/mcp-connect-auth
    """

    def __init__(
        self,
        *,
        listing_slug: str,
        base_url: AnyHttpUrl | str,
        required_scopes: list[str] | None = None,
        scopes_supported: list[str] | None = None,
        resource_name: str | None = None,
        resource_documentation: AnyHttpUrl | None = None,
        token_verifier: TokenVerifier | None = None,
        public_config_base_url: str = DEFAULT_PUBLIC_CONFIG_BASE_URL,
        public_config: PublicConfig | None = None,
        public_config_fetcher: PublicConfigFetcher | None = None,
    ) -> None:
        if not listing_slug:
            raise ValueError("listing_slug is required")

        self.listing_slug = listing_slug
        self.public_config_base_url = public_config_base_url.rstrip("/")
        base_url_value = str(base_url).rstrip("/") + "/"

        fetcher = public_config_fetcher or fetch_public_config
        self.public_config = public_config or fetcher(
            listing_slug,
            public_config_base_url=self.public_config_base_url,
        )

        parsed_scopes = (
            parse_scopes(required_scopes) if required_scopes is not None else []
        )
        self.required_scopes = parsed_scopes

        issuer = self.public_config["issuer"]
        audiences = [
            self.public_config["origin_resource"],
            self.public_config["bundle_proxy_resource"],
        ]

        if token_verifier is None:
            token_verifier = JWTVerifier(
                jwks_uri=jwks_url(self.public_config_base_url, listing_slug),
                issuer=issuer,
                algorithm="ES256",
                audience=audiences,
                required_scopes=self.required_scopes or None,
            )

        tenant_as = AnyHttpUrl(tenant_base_url(self.public_config_base_url, listing_slug))
        advertised_scopes = scopes_supported
        if advertised_scopes is None:
            advertised_scopes = self.public_config.get("scopes_supported")

        super().__init__(
            token_verifier=token_verifier,
            authorization_servers=[tenant_as],
            base_url=base_url_value,
            scopes_supported=advertised_scopes,
            resource_name=resource_name,
            resource_documentation=resource_documentation
            or AnyHttpUrl(INTEGRATION_DOC_URL),
        )

    @property
    def telemetry_ingest_url(self) -> str | None:
        return self.public_config.get("telemetry_ingest_url")

    def default_middleware(self) -> list[Middleware]:
        ingest_url = self.telemetry_ingest_url
        if not ingest_url:
            return []
        return [
            McpbundlesHandshakeMiddleware(
                ingest_url=ingest_url,
                listing_slug=self.listing_slug,
            )
        ]

    def get_routes(
        self,
        mcp_path: str | None = None,
    ) -> list[Route]:
        routes = super().get_routes(mcp_path)
        metadata_url = oauth_authorization_server_metadata_url(
            self.public_config_base_url,
            self.listing_slug,
        )

        async def oauth_authorization_server_metadata(request):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(metadata_url)
                    response.raise_for_status()
                    return JSONResponse(response.json())
            except Exception as exc:
                logger.error(
                    "Failed to fetch MCP Connect Auth metadata for listing %s: %s",
                    self.listing_slug,
                    exc,
                )
                return JSONResponse(
                    {
                        "error": "server_error",
                        "error_description": (
                            "Failed to fetch MCP Connect Auth authorization server "
                            f"metadata for listing '{self.listing_slug}'. "
                            f"See {INTEGRATION_DOC_URL}."
                        ),
                    },
                    status_code=500,
                )

        routes.append(
            Route(
                "/.well-known/oauth-authorization-server",
                endpoint=oauth_authorization_server_metadata,
                methods=["GET"],
            )
        )
        return routes
