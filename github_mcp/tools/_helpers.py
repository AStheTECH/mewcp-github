"""Shared error helpers for all tool modules."""

from __future__ import annotations

from typing import Any

import httpx

from ..schemas import ToolError, ToolResult
from ..service import GitHubServiceError


def _err(
    result_class: type[ToolResult],
    tlog,
    code: str,
    message: str,
    status: int,
    retriable: bool = False,
    retry_after: int | None = None,
    details: dict[str, Any] | None = None,
) -> ToolResult:
    tlog.failure(code, message)
    return result_class(
        success=False,
        statusCode=status,
        retriable=retriable,
        retry_after_seconds=retry_after,
        error=ToolError(code=code, message=message, details=details),
    )


def _handle_service_exc(
    result_class: type[ToolResult],
    tlog,
    exc: Exception,
) -> ToolResult:
    """Handle GitHubServiceError, httpx request exceptions, and generic errors."""
    if isinstance(exc, GitHubServiceError):
        tlog.failure(exc.code, exc.message)
        return result_class(
            success=False,
            statusCode=exc.http_status or 400,
            retriable=exc.retryable,
            error=ToolError(code=exc.code, message=exc.message, details=exc.details),
        )
    if isinstance(exc, httpx.TimeoutException):
        tlog.failure("TIMEOUT", "Upstream API request timed out.")
        return result_class(
            success=False,
            statusCode=504,
            retriable=True,
            error=ToolError(
                code="TIMEOUT", message="Upstream API request timed out."
            ),
        )
    if isinstance(exc, httpx.ConnectError):
        tlog.failure("CONNECTION_ERROR", "Could not connect to upstream API.")
        return result_class(
            success=False,
            statusCode=503,
            retriable=True,
            error=ToolError(
                code="CONNECTION_ERROR", message="Could not connect to upstream API."
            ),
        )
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        tlog.failure("HTTP_ERROR", f"HTTP {status}")
        return result_class(
            success=False,
            statusCode=status,
            retriable=status >= 500,
            error=ToolError(
                code="HTTP_ERROR",
                message=f"HTTP {status}",
                details={"status_code": status},
            ),
        )
    tlog.failure("INTERNAL_ERROR", str(exc))
    return result_class(
        success=False,
        statusCode=500,
        retriable=False,
        error=ToolError(
            code="INTERNAL_ERROR",
            message="Unexpected error.",
            details={"exception": str(exc)},
        ),
    )
