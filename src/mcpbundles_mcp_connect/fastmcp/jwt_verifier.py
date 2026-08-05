"""Strict Connect Auth JWT verifier for FastMCP."""

from __future__ import annotations

from fastmcp.server.auth import AccessToken
from fastmcp.server.auth.providers.jwt import JWTVerifier


class McpbundlesJWTVerifier(JWTVerifier):
    """JWT verifier with JWKS kid retry and strict ``client_id`` handling.

    Connect Auth always mints ``client_id`` separately from ``sub``. This
    verifier does not fall back ``client_id`` to ``sub`` (unlike generic
    ``JWTVerifier``).
    """

    async def _get_jwks_key(self, kid: str | None) -> str:
        try:
            return await super()._get_jwks_key(kid)
        except ValueError as exc:
            message = str(exc)
            if kid and "not found in JWKS" in message:
                self._jwks_cache_time = 0.0
                return await super()._get_jwks_key(kid)
            raise

    async def load_access_token(self, token: str) -> AccessToken | None:
        access_token = await super().load_access_token(token)
        if access_token is None:
            return None

        claims = access_token.claims
        raw_client_id = claims.get("client_id") or claims.get("azp")
        if not isinstance(raw_client_id, str) or not raw_client_id.strip():
            self.logger.debug(
                "Bearer token rejected: Connect Auth token missing client_id claim"
            )
            return None

        if access_token.client_id != raw_client_id:
            return access_token.model_copy(update={"client_id": raw_client_id})
        return access_token
