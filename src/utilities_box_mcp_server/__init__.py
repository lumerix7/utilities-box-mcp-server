def main():
    import os
    import argparse

    if os.getenv("SIMP_LOGGER_LOG_FILE") is None:
        os.environ["SIMP_LOGGER_LOG_FILE"] = os.path.join(
            os.path.expanduser("~"), "logs", "utilities-box-mcp-server", "mcp.log")

    parser = argparse.ArgumentParser(
        description="Utilities Box MCP Server"
    )
    parser.add_argument("--transport", type=str,
                        help="Transport type, defaults to 'stdio', can be 'stdio' or 'see'. Use Environment variable 'UTILITIES_BOX_TRANSPORT' if not provided.")

    args = parser.parse_args()

    from .server import serve
    serve(transport=args.transport)


if __name__ == "__main__":
    main()
