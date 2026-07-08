from __future__ import annotations

import logging
import time


class ToolLogger:
    """Structured logger for tool calls with timing."""

    def __init__(self, logger: logging.Logger, tool_name: str) -> None:
        self._logger = logger
        self._tool_name = tool_name
        self._start = time.perf_counter()
        self._logger.info("tool=%s status=started", tool_name)

    def success(self) -> None:
        elapsed_ms = int((time.perf_counter() - self._start) * 1000)
        self._logger.info(
            "tool=%s status=ok duration_ms=%d", self._tool_name, elapsed_ms
        )

    def failure(self, code: str, message: str) -> None:
        elapsed_ms = int((time.perf_counter() - self._start) * 1000)
        self._logger.error(
            "tool=%s status=error code=%s duration_ms=%d msg=%s",
            self._tool_name,
            code,
            elapsed_ms,
            message,
        )
