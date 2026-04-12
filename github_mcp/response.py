from __future__ import annotations

from typing import Any


def success_response(
    tool: str, data: Any, meta: dict[str, Any] | None = None
) -> dict[str, Any]:
    payload_meta = {
        "tool": tool,
    }
    if meta:
        payload_meta.update(meta)

    return {
        "ok": True,
        "data": data,
        "error": None,
        "meta": payload_meta,
    }


def error_response(
    tool: str,
    *,
    code: str,
    message: str,
    http_status: int | None = None,
    retryable: bool = False,
    details: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload_meta = {
        "tool": tool,
    }
    if meta:
        payload_meta.update(meta)

    return {
        "ok": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "http_status": http_status,
            "retryable": retryable,
            "details": details or {},
        },
        "meta": payload_meta,
    }
