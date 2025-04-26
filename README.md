# utilities-box-mcp-server
A MCP Server with utilities and tools for various tasks, including time management, system information, and more.

See also:

* [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
* [Adding MCP to your python project](https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#adding-mcp-to-your-python-project)
* [modelcontextprotocol/python-sdk/tree/main/examples/fastmcp](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/fastmcp)
* [fastmcp](https://github.com/jlowin/fastmcp)



## 1. Install and run
### 1.1. Install using pip
```bash
# Uninstall the previous version
pip uninstall --yes utilities-box-mcp-server

pip install utilities-box-mcp-server --upgrade --force-reinstall --extra-index-url http://127.0.0.1:8081/repository/pypi-group/simple --trusted-host 127.0.0.1
```


### 1.2. Install from source
```bash
cd /path/to/your/project

pip install .
```


### 1.2. Run
```bash
# Run this server directly
utilities-box-mcp-server

# Or run this server using sse transport
export UTILITIES_BOX_PORT=41104
export UTILITIES_BOX_LOG_LEVEL=DEBUG
export UTILITIES_BOX_TRANSPORT=sse
utilities-box-mcp-server

# Or run with python
python -m utilities_box_mcp_server

# Or run with uv
uv run utilities-box-mcp-server
```



## 2. MCP configurations
**Available environment variables:**

| Name                      | Default value | Description                                                                                          |
|---------------------------|---------------|------------------------------------------------------------------------------------------------------|
| `UTILITIES_BOX_TRANSPORT` | `stdio`       | The transport type to use. Can be `stdio` or `sse`.                                                  |
| `UTILITIES_BOX_HOST`      | `0.0.0.0`     | The host to bind the server to(sse transport only).                                                  |
| `UTILITIES_BOX_PORT`      | `41104`       | The port to use for the server(sse transport only).                                                  |
| `UTILITIES_BOX_LOG_LEVEL` | `INFO`        | The log level to use(sse transport only). Can be `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`. |

**Command line usage:**

```bash
$ utilities-box-mcp-server --help
usage: utilities-box-mcp-server [-h] [--transport TRANSPORT] [--host HOST] [--port PORT] [--log-level LOG_LEVEL]

Utilities Box MCP Server

options:
  -h, --help            show this help message and exit
  --transport TRANSPORT
                        Transport type, defaults to 'stdio', can be 'stdio' or 'see'. Use Environment variable 'UTILITIES_BOX_TRANSPORT' if not provided.
  --host HOST           Host to bind to(sse transport only), defaults to '0.0.0.0'. Use Environment variable 'UTILITIES_BOX_HOST' if not provided.
  --port PORT           Port to bind to(sse transport only), defaults to '41104'. Use Environment variable 'UTILITIES_BOX_PORT' if not provided.
  --log-level LOG_LEVEL
                        Log level(sse transport only), defaults to 'INFO'. Use Environment variable 'UTILITIES_BOX_LOG_LEVEL' if not provided.
```


### 2.1. SSE
Example endpoint: `http://127.0.0.1:41102/sse`


### 2.2. stdio
JSON:

```json
{
  "utilities-box": {
    "type": "stdio",
    "command": "uv",
    "args": [
      "run",
      "utilities-box-mcp-server"
    ]
  }
}
```

YAML:

```yaml
utilities-box:
  type: stdio
  command: uv
  args:
    - run
    - utilities-box-mcp-server
```


### 2.3. Run with Docker
See:

* [docker/run-in-docker.sh](docker/0.1.0/run-in-docker.sh)
* [docker/0.1.0/Dockerfile](docker/0.1.0/Dockerfile)
* [docker/0.1.0/build.sh](docker/0.1.0/build.sh)



## 3. Tools
### 3.1. Task and time management tools
1. `get_current_time`
   See also [modelcontextprotocol/servers/tree/main/src/time/src/mcp_server_time](https://github.com/modelcontextprotocol/servers/tree/main/src/time/src/mcp_server_time)

   Usage:

   ```
   Get current time with the specified timezone name(optional) and format(optional), defaults to local timezone and %Y-%m-%d %H:%M:%S.
   Returns the current time in the specified format with timezone name and offset if available.

   Args:
       timezone_name (str): The timezone name to use (e.g., 'Asia/Shanghai', 'America/San_Francisco'), optional. Defaults to local timezone.
       time_format (str):   The format of the current time, optional. Defaults to %Y-%m-%d %H:%M:%S.

   Returns:
       Current time(GetCurrentTimeResult): The current time in the specified format with timezone name and offset if available.

   Raises:
       ValueError: If the timezone name is invalid or if the format is invalid.
   ```

2. `get_unix_timestamp`

   Get current Unix timestamp as seconds since January 1, 1970 UTC (Epoch time).

3. `calc_time_diff`

   Usage:

   ```
   Calculate the difference between two times in the specified format.

   Args:
       start_time (str):   The start time in the specified format, required.
       end_time (str):     The end time in the specified format, required.
       time_format (str):  The format of the time, optional. Defaults to %Y-%m-%d %H:%M:%S.
       diff_unit (str):    The unit of time to return the difference in, optional, defaults to seconds. Can be microseconds, milliseconds, seconds, minutes, hours, days or weeks.

   Returns:
       Difference(float): The difference between the two times in the specified unit.

   Raises:
       ValueError: If the time format is invalid or if an invalid unit is provided.
   ```


### 3.2. System information and status tools
1. `get_system_info`

   Get system information, including system, node name, release, version, machine, processor, CPU count, memory total and swap total.

2. `get_system_stats`

   Get system stats, including boot time, CPU count, CPU percent, memory percent, memory total, memory used, memory free, swap percent, swap total, swap used and swap free.


### 3.3. Network tools
1. `ping`

   Ping a DNS name or IP address with the optional timeout and count. Results are details of the ping command.

2. `check_connectivity`

   Checks connectivity to a destination using curl command with optional timeout and proxy options. Results are descriptions of the connectivity status.


### Other tools
1. `evaluate`
   See also [githejie/mcp-server-calculator](https://github.com/githejie/mcp-server-calculator)

   Usage:

   ```
   Evaluate the given numeric expression with the given variables if any.

   Args:
       expression (str): The numeric expression to evaluate.
       variables (dict): The variables to use in the expression, if any.

   Returns:
       Result(float): The result of the evaluation.

   Raises:
       ValueError: If the expression is invalid or if there are any issues with the evaluation.
   ```

2. `sleep`

   See also [Garoth/sleep-mcp](https://github.com/Garoth/sleep-mcp).

   Usage:

   ```
   Sleep for a specified amount of time.

   Args:
       time_value (float): The time value to sleep for, in 'time_unit' units, required.
       time_unit (str):    The unit of time to sleep for, optional, defaults to seconds. Can be microseconds, milliseconds, seconds, minutes, hours, days or weeks.

   Returns:
       Message(str): A message indicating that the server has slept for the specified duration.

   Raises:
       ValueError: If time_value is not positive or if an invalid time unit is provided.
   ```

3. `generate_uuid`

   Usage:

   ```
   Generates one or multiple UUIDs with the specified version, defaults to one UUID of version 4 (random).

   Args:
       :param: count:     Number of UUIDs to generate.
       :param: version:   UUID version (1, 3, 4, or 5).
       :param: namespace: Namespace UUID for v3/v5 (required for those versions).
                          Must be a valid UUID string or one of the predefined namespaces: 'dns', 'url', 'oid', 'x500'.
       :param: name:      Name string for v3/v5 (required for those versions).

   Returns:
       List of UUID strings.

   Raises:
       ValueError: If the count is not a positive integer or if the version is not 1, 3, 4, or 5 or if the namespace or name is not provided for versions 3 and 5.
   ```
