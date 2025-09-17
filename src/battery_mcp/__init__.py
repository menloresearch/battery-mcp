from .server import serve as serve_stdio
from .http_server import serve as serve_http


def main():
    """Battery MCP - MCP for creative battery materials"""
    import asyncio
    import argparse

    parser = argparse.ArgumentParser(
        description="give a model the ability to make web requests"
    )
    parser.add_argument("--transport", type=str,
                        help="transport-type of server", default="stdio")
    parser.add_argument(
        "--http-port",
        type=int,
        default=22312,
        help="serving port for http server",
    )
    parser.add_argument("--http-host", type=str, default="0.0.0.0", help="")

    args = parser.parse_args()
    if args.transport == "stdio":
        asyncio.run(serve_stdio())
    elif args.transport == "http":
        serve_http(host=args.http_host, port=args.http_port)
    else:
        print(f"Transport protocol '{args.transport}' is not supported")


if __name__ == "__main__":
    main()
