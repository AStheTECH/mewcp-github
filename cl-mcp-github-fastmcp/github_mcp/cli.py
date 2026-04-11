import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CL GitHub MCP Server")
    parser.add_argument(
        "-t",
        "--transport",
        help="Transport method for MCP (stdio, sse, streamable-http)",
        default="streamable-http",
    )
    parser.add_argument("--host", help="Host to bind the server to", default=None)
    parser.add_argument(
        "--port", type=int, help="Port to bind the server to", default=None
    )
    return parser.parse_args()
