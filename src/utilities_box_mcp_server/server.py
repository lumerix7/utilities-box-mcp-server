import json
from typing import Callable, Awaitable, Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from .logger import get_logger
from .schema.exceptions import ToolError
from .tools import calc_time_diff, get_current_time, get_unix_timestamp, \
    get_system_info, get_system_stats, \
    read_lines, read_files, \
    check_connectivity, ping, \
    evaluate, generate_uuid, sleep, \
    calc_time_diff_tool_description, get_current_time_tool_description, get_unix_timestamp_tool_description, \
    get_system_info_tool_description, get_system_stats_tool_description, \
    read_lines_tool_description, read_files_tool_description, \
    check_connectivity_tool_description, ping_tool_description, \
    evaluate_tool_description, generate_uuid_tool_description, sleep_tool_description, \
    calc_time_diff_tool_schema, get_current_time_tool_schema, get_unix_timestamp_tool_schema, \
    get_system_info_tool_schema, get_system_stats_tool_schema, \
    read_lines_tool_schema, read_files_tool_schema, \
    check_connectivity_tool_schema, ping_tool_schema, \
    evaluate_tool_schema, generate_uuid_tool_schema, sleep_tool_schema


def serve(transport: str | None = None) -> None:
    import os
    log = get_logger()

    available_tools: dict[str, Callable[..., Awaitable[Any]]] = {
        "calc_time_diff": calc_time_diff,
        "get_current_time": get_current_time,
        "get_unix_timestamp": get_unix_timestamp,
        "get_system_info": get_system_info,
        "get_system_stats": get_system_stats,
        "read_lines": read_lines,
        "read_files": read_files,
        "check_connectivity": check_connectivity,
        "ping": ping,
        "evaluate": evaluate,
        "generate_uuid": generate_uuid,
        "sleep": sleep,
    }
    tool_descriptions: dict[str, str] = {
        "calc_time_diff": calc_time_diff_tool_description,
        "get_current_time": get_current_time_tool_description,
        "get_unix_timestamp": get_unix_timestamp_tool_description,
        "get_system_info": get_system_info_tool_description,
        "get_system_stats": get_system_stats_tool_description,
        "read_lines": read_lines_tool_description,
        "read_files": read_files_tool_description,
        "check_connectivity": check_connectivity_tool_description,
        "ping": ping_tool_description,
        "evaluate": evaluate_tool_description,
        "generate_uuid": generate_uuid_tool_description,
        "sleep": sleep_tool_description,
    }
    tools_schemas: dict[str, dict[str, Any]] = {
        "calc_time_diff": calc_time_diff_tool_schema,
        "get_current_time": get_current_time_tool_schema,
        "get_unix_timestamp": get_unix_timestamp_tool_schema,
        "get_system_info": get_system_info_tool_schema,
        "get_system_stats": get_system_stats_tool_schema,
        "read_lines": read_lines_tool_schema,
        "read_files": read_files_tool_schema,
        "check_connectivity": check_connectivity_tool_schema,
        "ping": ping_tool_schema,
        "evaluate": evaluate_tool_schema,
        "generate_uuid": generate_uuid_tool_schema,
        "sleep": sleep_tool_schema,
    }
    tools_output_schemas: dict[str, dict[str, Any]] = {
        # "get_current_time": get_current_time_tool_output_schema,
        # "read_lines": read_lines_tool_output_schema,
        # "read_files": read_files_tool_output_schema,
        # "generate_uuid": generate_uuid_tool_output_schema,
    }

    server_name: str = os.getenv("UTILITIES_BOX_MCP_SERVER_NAME", "Utilities Box MCP Server")
    enabled_tools_str: str = os.getenv("UTILITIES_BOX_ENABLED_TOOLS", "")
    enabled_tools: list[str] = [tool.strip() for tool in enabled_tools_str.split(",") if tool.strip()]
    disable_tool_str: str = os.getenv("UTILITIES_BOX_DISABLED_TOOLS", "")
    disabled_tools: list[str] = [tool.strip() for tool in disable_tool_str.split(",") if tool.strip()]

    tools: dict[str, Callable[..., Awaitable[Any]]] = {}
    for tool_name, tool_func in available_tools.items():
        if (not enabled_tools or tool_name in enabled_tools) \
                and (not disabled_tools or tool_name not in disabled_tools):
            tools[tool_name] = tool_func
        elif disabled_tools and tool_name in disabled_tools:
            log.warning(f"Tool '{tool_name}' is disabled and will not be available")
        elif enabled_tools and tool_name not in enabled_tools:
            log.warning(f"Tool '{tool_name}' is not in the list of enabled tools and will not be available")

    log.info(f"Enabling tools: {', '.join(tools.keys()) if tools else 'No tools enabled'}")

    server = Server(server_name)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        result = []
        for name in tools.keys():
            result.append(Tool(
                name=name,
                description=tool_descriptions[name],
                inputSchema=tools_schemas[name],
                outputSchema=tools_output_schemas.get(name, None),
            ))
        return result

    @server.call_tool()
    async def call_tool(name: str, args: dict) -> Any:
        if name not in tools:
            raise ToolError(message=f"Tool '{name}' is not available", code=400)
        try:
            result = tools[name](**args)
            import asyncio
            if asyncio.iscoroutine(result):
                result = await result

            log.debug(f"Tool '{name}' returned result: {result}, type: {type(result)}")

            structured: dict[str, Any] | None = None
            unstructured: Any = None
            output_schema: dict[str, Any] | None = tools_output_schemas.get(name, None)

            if output_schema is not None:
                if isinstance(result, BaseModel):
                    structured = result.model_dump()
                    unstructured = [TextContent(type="text", text=json.dumps(structured, ensure_ascii=False, indent=2))]
                elif isinstance(result, dict):
                    structured = result
                    unstructured = [TextContent(type="text", text=json.dumps(structured, ensure_ascii=False, indent=2))]
                elif isinstance(result, str):
                    unstructured = [TextContent(type="text", text=result)]
                elif isinstance(result, list):
                    unstructured = [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
                else:
                    unstructured = [TextContent(type="text", text=str(result))]
            else:
                if isinstance(result, BaseModel):
                    d = result.model_dump()
                    unstructured = [TextContent(type="text", text=json.dumps(d, ensure_ascii=False, indent=2))]
                elif isinstance(result, (dict, list)):
                    unstructured = [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
                elif isinstance(result, str):
                    unstructured = [TextContent(type="text", text=result)]
                else:
                    unstructured = [TextContent(type="text", text=str(result))]

            ret_val: Any = unstructured if structured is None else (unstructured, structured)
            log.debug(f"Tool '{name}' finally returning value: {ret_val}, type: {type(ret_val)}")
            return ret_val
        except ToolError as e:
            raise e
        except BaseException as e:
            import traceback
            log.error(f"Error calling tool '{name}': {e}:\n{traceback.format_exc()}")
            raise ToolError(message=f"Error calling tool '{name}': {e}", code=500)

    options = server.create_initialization_options()

    if transport is None or not transport:
        transport = os.getenv("UTILITIES_BOX_TRANSPORT", "stdio")

    if transport == "sse":
        sse_bind_host = os.getenv("UTILITIES_BOX_SSE_BIND_HOST", "0.0.0.0")
        sse_port = int(os.getenv("UTILITIES_BOX_SSE_PORT", "41104"))
        sse_debug_enabled = os.getenv("UTILITIES_BOX_SSE_DEBUG_ENABLED", "false").lower() == "true"
        sse_transport_endpoint = os.getenv("UTILITIES_BOX_SSE_TRANSPORT_ENDPOINT", "/messages/")

        log.info(f"Starting server with SSE transport on {sse_bind_host}:{sse_port}... "
                 f"debug = {sse_debug_enabled}, transport endpoint = {sse_transport_endpoint}")

        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route
        import uvicorn

        async def handle_sse(request):
            async with sse.connect_sse(
                    request.scope, request.receive, request._send
            ) as streams:
                await server.run(streams[0], streams[1], options)

        sse = SseServerTransport(sse_transport_endpoint)

        routes = [
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ]

        starlette_app = Starlette(debug=sse_debug_enabled, routes=routes)
        uvicorn.run(starlette_app, host=sse_bind_host, port=sse_port)
    else:
        import os

        if os.getenv("SIMP_LOGGER_LOG_CONSOLE_ENABLED", "True").lower() != "false":
            log.error("SIMP_LOGGER_LOG_CONSOLE_ENABLED must be set to False to use stdio transport")
            raise ToolError(message="SIMP_LOGGER_LOG_CONSOLE_ENABLED must be set to False to use stdio transport",
                            code=400)

        log.info(f"Starting server with stdio transport...")

        from mcp import stdio_server

        async def run_stdio_server():
            async with stdio_server() as (read_stream, write_stream):
                await server.run(read_stream, write_stream, options)

        import asyncio

        asyncio.run(run_stdio_server())
