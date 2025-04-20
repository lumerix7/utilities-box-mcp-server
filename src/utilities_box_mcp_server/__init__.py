from .server import serve


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Utilities Box MCP Server"
    )

    parser.add_argument("--transport", type=str, help="Transport type, defaults to 'stdio', can be 'stdio' or 'see'. Use Environment variable 'UTILITIES_BOX_TRANSPORT' if not provided.")
    parser.add_argument("--host", type=str, help="Host to bind to(sse transport only), defaults to '0.0.0.0'. Use Environment variable 'UTILITIES_BOX_HOST' if not provided.")
    parser.add_argument("--port", type=int, help="Port to bind to(sse transport only), defaults to '41104'. Use Environment variable 'UTILITIES_BOX_PORT' if not provided.")
    parser.add_argument("--log-level", type=str, help="Log level(sse transport only), defaults to 'INFO'. Use Environment variable 'UTILITIES_BOX_LOG_LEVEL' if not provided.")

    args = parser.parse_args()
    serve(
        transport=args.transport,
        host=args.host,
        port=args.port,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()
