# utilities-box-mcp-server
A MCP Server with utilities and tools for various tasks, including time management, system information, and more.

See also:

* [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
* [Adding MCP to your python project](https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#adding-mcp-to-your-python-project)



## Install and run
### Install using pip
```bash
# Uninstall the previous version
pip uninstall --yes utilities-box-mcp-server

pip install utilities-box-mcp-server --upgrade --force-reinstall --extra-index-url http://127.0.0.1:8081/repository/pypi-group/simple --trusted-host 127.0.0.1
```


### Install from source
```bash
cd /path/to/your/project

pip install .
```


### Run
```bash
# Run this server directly
utilities-box-mcp-server

# Or run this server using sse transport
export UTILITIES_BOX_PORT=41104
export UTILITIES_BOX_TRANSPORT=sse
utilities-box-mcp-server

# Or run with python
python -m utilities_box_mcp_server

# Or run with uv
uv run utilities-box-mcp-server
```



## MCP configurations
**Available environment variables:**

| Name                              | Default value              | Description                                                                                                                                                                                                                                                                                |
|-----------------------------------|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `UTILITIES_BOX_MCP_SERVER_NAME`   | `Utilities Box MCP Server` | Name of the MCP server.                                                                                                                                                                                                                                                                    |
| `UTILITIES_BOX_ENABLED_TOOLS`     | *Empty*                    | Comma-separated list of enabled tools. If empty, all tools are enabled. Available tools: `calc_time_diff`, `check_connectivity`, `evaluate`, `generate_uuid`, `get_current_time`, `get_system_info`, `get_system_stats`, `get_unix_timestamp`, `ping`, `read_file`, `read_files`, `sleep`. |
| `UTILITIES_BOX_DISABLED_TOOLS`    | *Empty*                    | Comma-separated list of disabled tools. If empty, no tools are disabled. See `UTILITIES_BOX_ENABLED_TOOLS` for available tools.                                                                                                                                                            |
| `UTILITIES_BOX_SSE_BIND_HOST`     | `0.0.0.0`                  | Host to bind the server to (sse transport only).                                                                                                                                                                                                                                           |
| `UTILITIES_BOX_TRANSPORT`         | `stdio`                    | Transport type to use. Can be `stdio` or `sse`.                                                                                                                                                                                                                                            |
| `UTILITIES_BOX_HOST`              | `0.0.0.0`                  | Host to bind the server to (sse transport only).                                                                                                                                                                                                                                           |
| `UTILITIES_BOX_PORT`              | `41104`                    | Port to use for the server (sse transport only).                                                                                                                                                                                                                                           |
| `UTILITIES_BOX_SSE_DEBUG_ENABLED` | `false`                    | Enable debug mode for sse transport (sse transport only).                                                                                                                                                                                                                                  |
| `SIMP_LOGGER_LOG_CONSOLE_ENABLED` | `true`                     | Enable logging to console, **MUST** DISABLED if using `stdio` transport.                                                                                                                                                                                                                   |

**Command line usage:**

```bash
$ utilities-box-mcp-server --help
usage: utilities-box-mcp-server [-h] [--transport TRANSPORT]

Utilities Box MCP Server

options:
  -h, --help            show this help message and exit
  --transport TRANSPORT
                        Transport type, defaults to 'stdio', can be 'stdio' or 'see'. Use Environment variable 'UTILITIES_BOX_TRANSPORT' if not provided.
```


### sse
Example endpoint: `http://127.0.0.1:41102/sse`


### stdio
JSON:

```json
{
  "utilities-box": {
    "type": "stdio",
    "command": "utilities-box-mcp-server",
    "args": [],
    "env": {
      "SIMP_LOGGER_LOG_CONSOLE_ENABLED": "false",
      "UTILITIES_BOX_SSE_DEBUG_ENABLED": "true",
      "UTILITIES_BOX_TRANSPORT": "stdio"
    }
  }
}
```

Or:

```json
{
  "utilities-box": {
    "type": "stdio",
    "command": "uv",
    "args": [
      "run",
      "utilities-box-mcp-server"
    ],
    "env": {
      "SIMP_LOGGER_LOG_CONSOLE_ENABLED": "false",
      "UTILITIES_BOX_SSE_DEBUG_ENABLED": "true",
      "UTILITIES_BOX_TRANSPORT": "stdio"
    }
  }
}
```

YAML:

```yaml
utilities-box:
  type: stdio
  command: utilities-box-mcp-server
  args: [ ]
  env:
    SIMP_LOGGER_LOG_CONSOLE_ENABLED: "false"
    UTILITIES_BOX_SSE_DEBUG_ENABLED: "true"
    UTILITIES_BOX_TRANSPORT: "stdio"
```


### Run with Docker
See:

* [docker/run-utilities-box-mcp-server-in-docker.sh](docker/0.1.0/run-utilities-box-mcp-server-in-docker.sh)
* [docker/0.1.0/Dockerfile](docker/0.1.0/Dockerfile)
* [docker/0.1.0/build.sh](docker/0.1.0/build.sh)



## Tools
### Task and time management tools
1. `calc_time_diff`

   Calculates the difference between two times in the specified format.

2. `get_current_time`

   Gets current time with the specified timezone name(optional) and format(optional),
   defaults to local timezone and %Y-%m-%d %H:%M:%S.
   Returns the current time in the specified format with timezone name and offset if available.

3. `get_unix_timestamp`

   Gets the current Unix timestamp as seconds since January 1, 1970 UTC (Epoch time).


### System information and status tools
1. `get_system_info`

   Gets system information, including system, node name, release, version, machine, processor, CPU count, memory total,
   and swap total.

2. `get_system_stats`

   Gets system stats, including boot time, CPU count, CPU percent, memory percent, memory total, memory used,
   memory free, swap percent, swap total, swap used, and swap free.


### File system tools
1. `read_lines`

   Reads the lines of a file with a max bytes limit of 10MB. Returns it as a list of strings in utf-8 encoding.

2. `read_files`

   Reads all content of one or multiple files with a max size limit of 10MB per file.
   Returns a content_list with the item of file_path and content in utf-8 encoding.


### Network tools
1. `check_connectivity`

   Checks connectivity to a destination using curl command with optional timeout and proxy options.
   Returns a description of the connectivity status.

2. `ping`

   Pings a DNS name or IP address with the optional timeout and count. Returns details of the ping command.


### Other tools
1. `evaluate`

   Evaluates the given numeric expression with the given variables (if any).
   Returns numerical value of the expression.

2. `generate_uuid`

   Generates one or multiple UUIDs with the specified version, defaults to one UUID of version 4 (random).
   Returns a list of UUID strings.

3. `sleep`

   Sleeps for a specified amount of time.
