#!/usr/bin/env python3
"""MCP Server for GitHub API."""

import logging

from fastmcp import FastMCP
from fastmcp_credentials import CredentialMiddleware, HeaderCredentialBackend
from starlette.responses import JSONResponse

from github_mcp.cli import parse_args
from github_mcp.config import BREAKING_CHANGES, SERVER_VERSION, configure_logging
from github_mcp.tools import register_tools

configure_logging()
logger = logging.getLogger("github-mcp-server")

backend = HeaderCredentialBackend()
mcp = FastMCP(
    "MewCP GitHub MCP Server",
    version=SERVER_VERSION,
    middleware=[CredentialMiddleware(backend, "oauth")],
)
register_tools(mcp)


# /health MUST come before mcp.http_app() — routes are baked at http_app() time
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({
        "status": "healthy",
        "service": mcp.name,
        "version": SERVER_VERSION,
        "breaking_changes": BREAKING_CHANGES,
    })


# Expose ASGI app for hosted runtimes.
app = mcp.http_app(path="/mcp", transport="streamable-http", stateless_http=True)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("GitHub MCP Server Starting")
    logger.info("=" * 60)

    args = parse_args()

    run_kwargs = {}
    if args.transport:
        run_kwargs["transport"] = args.transport
        logger.info("Transport: %s", args.transport)
    if args.host:
        run_kwargs["host"] = args.host
        logger.info("Host: %s", args.host)
    if args.port:
        run_kwargs["port"] = args.port
        logger.info("Port: %s", args.port)

    try:
        mcp.run(**run_kwargs)
    except KeyboardInterrupt:
        logger.info("Server stopped !")
    except Exception as exc:
        logger.error("Server crashed: %s", exc, exc_info=True)
        raise
