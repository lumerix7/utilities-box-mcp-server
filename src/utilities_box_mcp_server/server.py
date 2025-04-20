# server.py

import os
import sys
import time
from sys import stderr
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .schema import GetCurrentTimeResult, GenerateUUIDResult

# Create an MCP server
mcp = FastMCP("Utilities Box")


# Task and time management tools.

@mcp.tool(name="get_current_time",
          description="Get current time with the specified format(optional) and timezone nam(optional), defaults to local timezone and ISO format. "
                      "Returns the current time in the specified format with timezone name and offset if available.")
def get_current_time(
        timezone_name: Annotated[str, Field(
            description="The timezone name to use (e.g., 'Asia/Shanghai', 'America/San_Francisco'), optional. Defaults to local timezone.")] = None,
        time_format: Annotated[str, Field(
            description="The format of the current time, optional. Defaults to ISO format, i.e. %Y-%m-%dT%H:%M:%S%z.")] = "%Y-%m-%dT%H:%M:%S%z",
) -> Annotated[
    GetCurrentTimeResult, Field(description="The current time in the specified format with timezone name and offset.")]:
    """Retrieves current time with the specified format(optional) and timezone name(optional), defaults to local timezone and ISO format.
    Returns the current time in the specified format with timezone name and offset if available.

    Args:
        timezone_name (str): The timezone name to use, optional. Defaults to local timezone.
        time_format (str):   The format of the current time, optional. Defaults to ISO format, i.e. %Y-%m-%dT%H:%M:%S%z.

    Returns:
        Current time(GetCurrentTimeResult): The current time in the specified format with timezone name and offset if available.

    Raises:
        ValueError: If the timezone name is invalid or if the format is invalid.
    """

    # Check if the timezone name is valid
    if timezone_name is not None and not isinstance(timezone_name, str):
        raise ValueError("Timezone name must be a string")

    # Check if the format is valid
    if not isinstance(time_format, str):
        raise ValueError("Format must be a string")

    from datetime import datetime
    import tzlocal

    # Get local timezone from using tzlocal
    local_tz = tzlocal.get_localzone()

    # If a timezone name is provided, and it is not the local timezone, convert the current time to that timezone
    if timezone_name:
        try:
            if local_tz is None:
                raise ValueError("Local timezone is not available")

            # Compare the timezone name with the local timezone
            if timezone_name != str(local_tz):
                from zoneinfo import ZoneInfo

                # Convert the current time to the specified timezone
                target_timezone = ZoneInfo(timezone_name)

                now = datetime.now(local_tz).astimezone(target_timezone)
                utcoffset = now.utcoffset()

                return GetCurrentTimeResult(
                    datetime=now.strftime(time_format),
                    tz_name=timezone_name,
                    tz_offset=int(utcoffset.total_seconds()) if utcoffset is not None else None
                )

        except Exception as e:
            raise ValueError(f"Error getting current time in timezone '{timezone_name}': {e}")

    # Get the local time in the specified format
    now = datetime.now(local_tz)
    local_utcoffset = now.utcoffset()

    return GetCurrentTimeResult(
        datetime=now.strftime(time_format),
        tz_name=str(local_tz) if local_tz else None,
        tz_offset=int(local_utcoffset.total_seconds()) if local_utcoffset else None
    )


@mcp.tool(name="get_unix_timestamp",
          description="Get current Unix timestamp as seconds since January 1, 1970 UTC (Epoch time).")
def get_unix_timestamp() -> Annotated[
    int, Field(description="The current time Unix timestamp as seconds since January 1, 1970 UTC (Epoch time).")]:
    # Get the current time unix timestamp
    from datetime import datetime

    # Get the current time in seconds since epoch
    return int(datetime.now().timestamp())


@mcp.tool(name="calc_time_diff", description="Calculate the difference between two times in the specified format.")
def calc_time_diff(
        start_time: Annotated[str, Field(description="The start time in the specified format, required.")],
        end_time: Annotated[str, Field(description="The end time in the specified format, required.")],
        time_format: Annotated[str, Field(
            description="The format of the time, optional. Defaults to ISO format, i.e. %Y-%m-%dT%H:%M:%S%z.")] = "%Y-%m-%dT%H:%M:%S%z",
        diff_unit: Annotated[str, Field(
            description="The unit of time to return the difference in, optional, defaults to seconds. Can be microseconds, milliseconds, seconds, minutes, hours, days or weeks.")] = "seconds",
) -> Annotated[float, Field(description="The difference between the two times in the specified unit.")]:
    """Calculates the difference between two times in the specified format.

    Args:
        start_time (str):   The start time in the specified format, required.
        end_time (str):     The end time in the specified format, required.
        time_format (str):  The format of the time, optional. Defaults to ISO format, i.e. %Y-%m-%dT%H:%M:%S%z.
        diff_unit (str):    The unit of time to return the difference in, optional, defaults to seconds. Can be microseconds, milliseconds, seconds, minutes, hours, days or weeks.

    Returns:
        Difference(float): The difference between the two times in the specified unit.

    Raises:
        ValueError: If the time format is invalid or if an invalid unit is provided.
    """

    # Dictionary of conversion factors to convert any time unit to seconds
    conversion_factors = {
        "microseconds": 0.000001,
        "milliseconds": 0.001,
        "seconds": 1,
        "minutes": 60,
        "hours": 3600,
        "days": 86400,
        "weeks": 604800,
    }

    # Check if the provided time format is valid
    if not isinstance(time_format, str):
        raise ValueError("Time format must be a string")

    # Check if the provided unit is valid
    if diff_unit not in conversion_factors:
        valid_units = ", ".join(f'"{unit}"' for unit in conversion_factors.keys())
        raise ValueError(f"Invalid unit. Please use one of: {valid_units}")

    # Import datetime and parse the start and end times
    from datetime import datetime

    try:
        start_dt = datetime.strptime(start_time, time_format)
        end_dt = datetime.strptime(end_time, time_format)
    except ValueError as e:
        raise ValueError(f"Error parsing date/time: {e}")

    # Calculate the difference between the two times
    delta = end_dt - start_dt

    # Convert the difference to seconds based on the specified unit
    return delta.total_seconds() / conversion_factors[diff_unit]


# System information and status tools.

@mcp.tool(name="get_system_info",
          description="Get system information, including system, node name, release, version, machine, processor, CPU count, memory total and swap total.")
def get_system_info() -> Annotated[dict, Field(description="A dictionary containing system information.")]:
    import platform
    import psutil

    pm = psutil.virtual_memory()
    swap = psutil.swap_memory()

    system_info = {
        "system": platform.system(),
        "node_name": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": psutil.cpu_count(logical=True),
        "memory_total": pm.total if pm else None,
        "swap_total": swap.total if swap else None,
    }

    return system_info


@mcp.tool(name="get_system_stats",
          description="Get system stats, including boot time, CPU count, CPU percent, memory percent, memory total, memory used, memory free, swap percent, swap total, swap used and swap free.")
async def get_system_stats() -> Annotated[dict, Field(description="A dictionary containing system stats.")]:
    import psutil

    pm = psutil.virtual_memory()
    swap = psutil.swap_memory()

    system_stats = {
        "boot_time": psutil.boot_time(),
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": pm.percent if pm else None,
        "memory_total": pm.total if pm else None,
        "memory_used": pm.used if pm else None,
        "memory_free": pm.free if pm else None,
        "swap_percent": swap.percent if swap else None,
        "swap_total": swap.total if swap else None,
        "swap_used": swap.used if swap else None,
        "swap_free": swap.free if swap else None,
    }

    return system_stats


# Network tools.

@mcp.tool(name="ping",
          description="Ping a DNS name or IP address with the optional timeout and count. Results are details of the ping command.")
async def ping(destination: Annotated[str, Field(description="The DNS name or IP address to ping, required.")],
               timeout: Annotated[int | float, Field(description="The total timeout for the ping in seconds, optional, "
                                                                 "defaults to 15 seconds.")] = 15.0,
               count: Annotated[int, Field(description="The number of pings to send, optional, defaults to 3.")] = 3,
               ) -> Annotated[str, Field(description="The details of the ping command.")]:
    """Ping a DNS name or IP address with the optional timeout and count.
    Args:
        :param destination: (str) The DNS name or IP address to ping, required.
        :param timeout: (float):  The timeout for the ping in seconds, optional, defaults to 15 seconds.
        :param count: (int):      The number of pings to send, optional, defaults to 3.

    Returns:
        :return: (str): The details of the ping command.

    Raises:
        ValueError: If the destination, timeout or count is invalid.
    """

    # Check destination
    if not destination or not isinstance(destination, str) or not destination.strip():
        raise ValueError("Destination must be a non-empty DNS name or IP address")
    destination = destination.strip()
    # Check timeout
    if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 120:
        raise ValueError("Timeout must be a positive number between 0 and 120 seconds")
    # Check count
    if not isinstance(count, int) or count < 1 or count > 100:
        raise ValueError("Count must be a positive integer between 1 and 100")

    import platform
    import subprocess
    from subprocess import TimeoutExpired

    # Determine the ping command based on the operating system
    # Windows uses '-n', Linux/macOS uses '-c'
    # Linux/macOS uses '-W' for timeout (in seconds), '-w' flag for deadline, Windows uses '-w' (milliseconds)
    system = platform.system().lower()
    timeout_flag = '-w'
    if system == 'windows':
        param_count = '-n'
        # Convert seconds to milliseconds for Windows
        timeout *= 1000
    else:
        param_count = '-c'

    cmd = ['ping', param_count, str(count)]
    cmd += [timeout_flag, str(int(timeout))]
    cmd.append(destination)

    try:
        stderr.write(f"Pinging {destination}: {' '.join(cmd)}.\n")

        completed = subprocess.run(
            cmd,
            timeout=timeout + 1.0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )

        # Check if the ping command was successful
        if completed.returncode != 0:
            raise RuntimeError(f"Error while pinging {destination} (code {completed.returncode}):\n"
                               f"{completed.stderr.decode('utf-8').strip() if completed.stderr else 'No error message'}")

        result = completed.stdout.decode('utf-8').strip() if completed.stdout else None
        if not result:
            raise RuntimeError(f"No result from ping command for {destination}")

        return result

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Ping command not found on this system: {e}")
    except TimeoutExpired as e:
        raise TimeoutError(f"Ping to {destination} timed out after {timeout} seconds: {e}")


@mcp.tool(name="check_connectivity",
          description="Checks connectivity to a destination using curl command with optional timeout and proxy options. Results are descriptions of the connectivity status.")
async def check_connectivity(
        destination: Annotated[
            str,
            Field(description="The destination to check connectivity to, required, can be a hostname, IP address, "
                              "or URL.")
        ],
        timeout: Annotated[
            int | float,
            Field(description="The timeout for the telnet in seconds, optional, defaults to 15 seconds.")
        ] = 15.0,
        proxy_enabled: Annotated[
            bool,
            Field(description="Whether to enable the proxy settings, optional, defaults to False.")
        ] = True,
        proxy: Annotated[
            str,
            Field(description="The proxy server to use, optional, defaults to system proxy settings.")
        ] = None,
        proxy_username: Annotated[
            str,
            Field(description="The username for the proxy server, optional, defaults to system proxy settings.")
        ] = None,
        proxy_password: Annotated[
            str,
            Field(description="The password for the proxy server, optional, defaults to system proxy settings.")
        ] = None,
) -> Annotated[str, Field(description="The description of the connectivity status.")]:
    """Checks connectivity to a destination using curl command.

    Args:
        :param destination: (str):     The destination to check connectivity to, required, can be a hostname, IP address, or URL.
        :param timeout: (int | float): The timeout for the telnet in seconds, optional, defaults to 15 seconds.
        :param proxy_enabled: (bool):  Whether to enable the proxy settings, optional, defaults to True.
        :param proxy: (str):           The proxy server to use, optional, defaults to system proxy settings.
        :param proxy_username: (str):  The username for the proxy server, optional, defaults to system proxy settings.
        :param proxy_password: (str):  The password for the proxy server, optional, defaults to system proxy settings.

    Returns:
        The description of the connectivity status.

    Raises:
        ValueError: If the destination is invalid.
    """

    if not destination or not isinstance(destination, str) or not destination.strip():
        raise ValueError("Destination must be a non-empty DNS name or IP address")

    # Build the curl command
    cmd = ["curl", "--head", "--connect-timeout", str(timeout)]

    if proxy_enabled:
        if proxy and isinstance(proxy, str) and proxy.strip():
            cmd += ["--proxy", proxy]
        if proxy_username and isinstance(proxy_username, str) and proxy_username.strip():
            proxy_user = proxy_username if proxy_password is None \
                                           or not isinstance(proxy_password, str) or not proxy_password.strip() \
                else f"{proxy_username}:{proxy_password}"
            cmd += ["--proxy-user", proxy_user]
    else:
        # Parse the destination to extract the host
        import re

        if re.match(r'^\w+://', destination):
            from urllib.parse import urlparse
            parsed_url = urlparse(destination)
            host = parsed_url.netloc
        else:
            host = destination.strip()

        if host.count(':') > 0:
            host = host.split(':')[0]

        cmd += ["--noproxy", host]

    cmd += ["--insecure", "--proxy-insecure"]

    cmd.append(destination)

    import subprocess
    from subprocess import TimeoutExpired

    try:
        stderr.write(f"Checking connectivity to {destination}: {' '.join(cmd)}.\n")

        completed = subprocess.run(
            cmd,
            timeout=timeout + 1.0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )

        # Check if the curl command was successful
        error = completed.stderr.decode('utf-8').strip() if completed.stderr else None
        if completed.returncode in (7, 28):
            raise RuntimeError(f"Error while checking connectivity to {destination} (code {completed.returncode}):\n"
                               f"{error if error else 'No error message'}")

        result = completed.stdout.decode('utf-8').strip() if completed.stdout else None

        return (
            f"Connectivity to {destination} is successful:\n"
            f"{result if result else 'No result from curl command'}"
            f"{'\n' + error if error else 'No error message'}"
        )

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Curl command not found on this system: {e}")
    except TimeoutExpired as e:
        raise TimeoutError(f"Connection to {destination} timed out after {timeout} seconds: {e}")


# Other tools.

@mcp.tool(name="sleep", description="Sleep for a specified amount of time.")
async def sleep(
        time_value: Annotated[
            int | float,
            Field(description="The time value to sleep for, in 'time_unit' units, required.")
        ],
        time_unit: Annotated[
            str,
            Field(description="The unit of time to sleep for, optional, defaults to seconds. "
                              "Can be microseconds, milliseconds, seconds, minutes, hours, days or weeks.")] = "seconds",
) -> str:
    """Sleeps for a specified amount of time.

    Args:
        time_value (int | float): The time value to sleep for, in 'time_unit' units, required.
        time_unit (str):          The unit of time to sleep for, optional, defaults to seconds. Can be microseconds, milliseconds, seconds, minutes, hours, days or weeks.

    Returns:
        Message(str): A message indicating that the server has slept for the specified duration.

    Raises:
        ValueError: If time_value is not positive or if an invalid time unit is provided.
    """

    # Dictionary of conversion factors to convert any time unit to seconds
    conversion_factors = {
        "microseconds": 0.000001,
        "milliseconds": 0.001,
        "seconds": 1,
        "minutes": 60,
        "hours": 3600,
        "days": 86400,
        "weeks": 604800,
    }

    # Check if time_value is positive
    if time_value <= 0:
        raise ValueError("Sleep duration must be a positive number")

    # Check if the provided time unit is valid
    if time_unit not in conversion_factors:
        valid_units = ", ".join(f'"{unit}"' for unit in conversion_factors.keys())
        raise ValueError(f"Invalid time unit. Please use one of: {valid_units}")

    # Convert the time value to seconds based on the specified unit
    sleep_duration_seconds = time_value * conversion_factors[time_unit]

    # Sleep for the calculated duration
    start_time = time.perf_counter()
    time.sleep(sleep_duration_seconds)
    end_time = time.perf_counter()
    elapsed = end_time - start_time

    # Return a message indicating the sleep duration in the specified unit
    sys.stderr.write(f"Actual sleep time: {elapsed:.6f} seconds.\n")
    return f"Server slept for {time_value} {time_unit}."


@mcp.tool(name="evaluate", description="Evaluate the given numeric expression with the given variables if any.")
def evaluate(
        expression: Annotated[str, Field(description="The numeric expression to evaluate, required.")],
        variables: Annotated[
            dict, Field(description="The variables to use in the expression, if any, optional.")] = None,
) -> float:
    """Evaluates the given numeric expression with the given variables if any.

    Args:
        expression (str): The numeric expression to evaluate.
        variables (dict): The variables to use in the expression, if any.

    Returns:
        Result(float): The result of the evaluation.

    Raises:
        ValueError: If the expression is invalid or if there are any issues with the evaluation.
    """

    # Check if the expression is valid
    if not isinstance(expression, str):
        raise ValueError("Expression must be a string")

    # Check if the variables are valid
    if variables is not None and not isinstance(variables, dict):
        raise ValueError("Variables must be a dictionary")

    # Evaluate the expression using numexpr
    try:
        import numexpr as ne

        result = ne.evaluate(expression, local_dict=variables)
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}")

    return float(result)


@mcp.tool(name="generate_uuid",
          description="Generate one or multiple UUIDs with the specified version, defaults to one UUID of version 4 (random).")
def generate_uuid(
        count: Annotated[int, Field(description="The number of UUIDs to generate, optional, defaults to 1.")] = 1,
        version: Annotated[
            int, Field(description="UUID version (1, 3, 4, or 5), optional, defaults to 4 (random).")] = 4,
        namespace: Annotated[str, Field(description="Namespace UUID (required for versions 3 and 5). "
                                                    "Must be a valid UUID string or one of the predefined namespaces: 'dns', 'url', 'oid', 'x500'.")] = None,
        name: Annotated[str, Field(description="Name string (required for versions 3 and 5).")] = None,
) -> GenerateUUIDResult:
    """Generates one or multiple UUIDs with the specified version, defaults to one UUID of version 4 (random).

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
    """

    if not isinstance(count, int) or count < 1:
        raise ValueError("Count must be a positive integer")

    import uuid

    if not isinstance(version, int) or version not in [1, 3, 4, 5]:
        raise ValueError("UUID version must be an integer of 1, 3, 4, or 5")

    if version in [3, 5]:
        if namespace is None or name is None:
            raise ValueError(f"Version {version} requires both namespace and name parameters")
        if not isinstance(namespace, str):
            namespace = str(namespace)
        if not isinstance(name, str):
            name = str(name)

        # Predefined namespace UUIDs
        predefined_namespaces = {
            "dns": uuid.NAMESPACE_DNS,
            "url": uuid.NAMESPACE_URL,
            "oid": uuid.NAMESPACE_OID,
            "x500": uuid.NAMESPACE_X500
        }

        # Check namespace
        if namespace not in predefined_namespaces:
            try:
                if namespace.startswith("urn:uuid:"):
                    namespace = namespace[9:]
                namespace = uuid.UUID(namespace)
            except ValueError:
                raise ValueError(
                    "Invalid namespace UUID string, must be a valid UUID string or one of the predefined namespaces: 'dns', 'url', 'oid', 'x500'")
        else:
            # Use the predefined namespace UUID
            namespace = predefined_namespaces[namespace]

    # Note, for UUID versions 3 and 5, the same namespace and name will always generate the same UUID.
    # This is expected behavior because these versions create deterministic UUIDs based on hashing the inputs.

    uuids = []
    for i in range(count):
        match version:
            case 1:
                # Time-based
                u = uuid.uuid1()
            case 3:
                # MD5 hash-based
                # Add iteration number to name to make each UUID unique
                modified_name = f"{name}_{i}" if count > 1 else name
                u = uuid.uuid3(namespace, modified_name)
            case 4:
                # Random
                u = uuid.uuid4()
            case 5:
                # SHA-1 hash-based
                # Add iteration number to name to make each UUID unique
                modified_name = f"{name}_{i}" if count > 1 else name
                u = uuid.uuid5(namespace, modified_name)

            case _:
                raise ValueError("UUID version must be 1, 3, 4, or 5")

        uuids.append(str(u))

    return GenerateUUIDResult(uuids=uuids)


def serve(transport: str | None = None,
          host: str | None = None,
          port: int | None = None,
          log_level: str | None = None,
          ) -> None:
    """Start the MCP server with the specified transport.

    Args:
        :param transport: (str | None): The transport to use, optional. Defaults to stdio. If UTILITIES_BOX_TRANSPORT environment variable is set, it will be used.
        :param host: (str | None):      The host to bind to(sse transport only), optional. Defaults to 0.0.0.0. If UTILITIES_BOX_HOST environment variable is set, it will be used.
        :param port: (int | None):      The port to bind to(sse transport only), optional. Defaults to 41104. If UTILITIES_BOX_PORT environment variable is set, it will be used.
        :param log_level: (str | None): The log level to use(sse transport only), optional. Defaults to INFO. If UTILITIES_BOX_LOG_LEVEL environment variable is set, it will be used.

    Raises:
        ValueError: If the transport is not 'stdio' or 'sse'.
    """

    if transport is None or not transport:
        transport = os.getenv("UTILITIES_BOX_TRANSPORT", "stdio")

    if transport:
        if not isinstance(transport, str) or transport.strip() not in ["stdio", "sse"]:
            raise ValueError(f"Invalid transport: {transport}, must be 'stdio' or 'sse'")
        transport = transport.strip()

    if transport and transport == 'sse':
        mcp.settings.host = os.getenv("UTILITIES_BOX_HOST", "0.0.0.0") if host is None or not host else host
        mcp.settings.port = int(os.getenv("UTILITIES_BOX_PORT", "41104")) if port is None or port < 1 else port
        mcp.settings.log_level = os.getenv("UTILITIES_BOX_LOG_LEVEL", "INFO") if log_level is None or not log_level \
            else log_level
        stderr.write(
            f"Starting MCP server on {mcp.settings.host}:{mcp.settings.port} using SSE transport, log level: {mcp.settings.log_level}.\n")

        mcp.run(transport='sse')
    else:
        stderr.write(f"Starting MCP server using stdio transport.\n")

        mcp.run(transport='stdio')
