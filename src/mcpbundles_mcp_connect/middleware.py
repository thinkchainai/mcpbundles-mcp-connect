"""Origin telemetry middleware for MCP Connect Auth."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
import mcp.types as mt
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext

logger = logging.getLogger(__name__)
DEFAULT_INGEST_TIMEOUT = 5.0


class McpbundlesHandshakeMiddleware(Middleware):
    """Fire-and-forget initialize cohort ingest for origin MCP clients."""

    def __init__(
        self,
        *,
        ingest_url: str,
        listing_slug: str,
        timeout: float = DEFAULT_INGEST_TIMEOUT,
    ) -> None:
        super().__init__()
        self.ingest_url = ingest_url
        self.listing_slug = listing_slug
        self.timeout = timeout

    async def on_initialize(
        self,
        context: MiddlewareContext[mt.InitializeRequest],
        call_next: CallNext[mt.InitializeRequest, mt.InitializeResult | None],
    ) -> mt.InitializeResult | None:
        asyncio.create_task(self._ingest_handshake(context))
        return await call_next(context)

    async def _ingest_handshake(
        self,
        context: MiddlewareContext[mt.InitializeRequest],
    ) -> None:
        payload = self._build_payload(context)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.ingest_url, json=payload)
                response.raise_for_status()
        except Exception:
            logger.warning(
                "MCP Connect Auth handshake ingest failed for listing %s",
                self.listing_slug,
                exc_info=True,
            )

    def _build_payload(
        self,
        context: MiddlewareContext[mt.InitializeRequest],
    ) -> dict[str, Any]:
        params = getattr(context.message, "params", None)
        client_info = getattr(params, "client_info", None) if params else None
        client_name = getattr(client_info, "name", None) if client_info else None
        client_version = getattr(client_info, "version", None) if client_info else None
        protocol_requested = getattr(params, "protocol_version", None) if params else None
        capabilities = getattr(params, "capabilities", None) if params else None

        payload: dict[str, Any] = {
            "listing_slug": self.listing_slug,
            "client_name": client_name,
            "client_version": client_version,
            "protocol_requested": protocol_requested,
        }
        if capabilities is not None:
            if hasattr(capabilities, "model_dump"):
                payload["capabilities"] = capabilities.model_dump(
                    mode="json",
                    exclude_none=True,
                )
            elif isinstance(capabilities, dict):
                payload["capabilities"] = capabilities
        return payload
