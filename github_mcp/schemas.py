from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic import Field as PydanticField

T = TypeVar("T")


class ToolError(BaseModel):
    """Error details returned by a tool."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ToolResult(BaseModel, Generic[T]):
    """Base result model for all tool responses."""

    success: bool = True
    statusCode: int = 200
    data: T | None = None
    retriable: bool = False
    retry_after_seconds: int | None = None
    error: ToolError | None = None

    model_config = ConfigDict(extra="allow")
