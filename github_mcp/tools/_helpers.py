from __future__ import annotations

import logging
from typing import Any

import httpx

from ..schemas import ToolError, ToolResult

logger = logging.getLogger("github-mcp-server")


def _err(code: str, message: str, details: dict[str, Any] | None = None) -> ToolResult:
    return ToolResult(
        success=False,
        statusCode=400,
        error=ToolError(code=code, message=message, details=details),
    )


def _handle_request_exc(
    tool_name: str, exc: Exception
) -> ToolResult:
    """Handle httpx request exceptions and return a ToolResult."""
    if isinstance(exc, httpx.TimeoutException):
        return ToolResult(
            success=False,
            statusCode=504,
            retriable=True,
            error=ToolError(
                code="TIMEOUT",
                message="Upstream API request timed out.",
            ),
        )
    if isinstance(exc, httpx.ConnectError):
        return ToolResult(
            success=False,
            statusCode=503,
            retriable=True,
            error=ToolError(
                code="CONNECTION_ERROR",
                message="Could not connect to upstream API.",
            ),
        )
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return ToolResult(
            success=False,
            statusCode=status,
            retriable=status >= 500,
            error=ToolError(
                code="HTTP_ERROR",
                message=f"HTTP {status}",
                details={"status_code": status},
            ),
        )
    return ToolResult(
        success=False,
        statusCode=500,
        retriable=False,
        error=ToolError(
            code="UNEXPECTED_ERROR",
            message=str(exc),
            details={"exception_type": type(exc).__name__},
        ),
    )


def _upstream_err(status: int, body: Any = None) -> ToolResult:
    return ToolResult(
        success=False,
        statusCode=status,
        retriable=status >= 500,
        error=ToolError(
            code="UPSTREAM_ERROR",
            message=f"HTTP {status}",
            details={"body": body} if body else None,
        ),
    )
