import os
import sys
import time
from typing import Annotated, Any

from pydantic import Field

from .logger import get_logger
from .schema import GetCurrentTimeResult, GenerateUUIDResult, \
    FileContent, ReadFilesResult, ReadLinesResult
from .schema.exceptions import ToolError

log = get_logger()

# Task and time management tools.

calc_time_diff_tool_description: str = "Calculates the difference between two times in the specified format."
calc_time_diff_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "start_time": {
            "type": "string",
            "description": "Start time in the specified format, required.",
        },
        "end_time": {
            "type": "string",
            "description": "End time in the specified format, required.",
        },
        "time_format": {
            "type": "string",
            "description": "Format of the time, optional. Defaults to %Y-%m-%d %H:%M:%S.",
        },
        "diff_unit": {
            "type": "string",
            "description": "Unit of time to return the difference in, optional, defaults to seconds. Can be microseconds, milliseconds, seconds, minutes, hours, days or weeks.",
        },
    },
    "required": ["start_time", "end_time"],
}


def calc_time_diff(
        start_time: Annotated[str, Field(description="Start time in the specified format, required.")],
        end_time: Annotated[str, Field(description="End time in the specified format, required.")],
        time_format: Annotated[str, Field(
            description="Format of the time, optional. Defaults to %Y-%m-%d %H:%M:%S.")] = "%Y-%m-%d %H:%M:%S",
        diff_unit: Annotated[str, Field(
            description="Unit of time to return the difference in, optional, defaults to seconds. Can be microseconds, milliseconds, seconds, minutes, hours, days or weeks.")] = "seconds",
) -> Annotated[float, Field(description="Difference between the two times in the specified unit.")]:
    """Raises:
        ValueError: If the time format is invalid, or if an invalid unit is provided.
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

    if not isinstance(time_format, str):
        log.error("Time format must be a string.")
        raise ToolError(message="Time format must be a string", code=400)

    if diff_unit not in conversion_factors:
        valid_units = ", ".join(f'"{unit}"' for unit in conversion_factors.keys())
        log.error(f"Invalid unit: {diff_unit}. Please use one of: {valid_units}")
        raise ToolError(message=f"Invalid unit: {diff_unit}. Please use one of: {valid_units}", code=400)

    from datetime import datetime

    try:
        start_dt = datetime.strptime(start_time, time_format)
        end_dt = datetime.strptime(end_time, time_format)
    except ValueError as e:
        import traceback
        log.error(f"Error parsing date/time: {e}:\n{traceback.format_exc()}")
        raise ToolError(message=f"Error parsing date/time: {e}", code=400)

    delta = end_dt - start_dt

    # Convert the difference to seconds based on the specified unit
    return delta.total_seconds() / conversion_factors[diff_unit]


get_current_time_tool_description: str = (
    "Gets current time with the specified timezone name(optional) and format(optional), "
    "defaults to local timezone and %Y-%m-%d %H:%M:%S. "
    "Returns the current time in the specified format with timezone name and offset if available.")
get_current_time_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "timezone_name": {
            "type": "string",
            "description": "Timezone name to use (e.g., 'Asia/Shanghai', 'America/San_Francisco'), optional. Defaults to local timezone.",
        },
        "time_format": {
            "type": "string",
            "description": "Format of the current time, optional. Defaults to %Y-%m-%d %H:%M:%S.",
        },
    },
    "required": [],
}
get_current_time_tool_output_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "datetime": {
            "type": "string",
            "description": "Current time in the specified format with timezone name and offset if available.",
        },
        "tz_name": {
            "type": "string",
            "description": "Timezone name, optional.",
        },
        "tz_offset": {
            "type": "integer",
            "description": "Timezone offset in seconds, optional.",
        },
    },
    "required": [],
}


def get_current_time(
        timezone_name: Annotated[str, Field(
            description="Timezone name to use (e.g., 'Asia/Shanghai', 'America/San_Francisco'), optional. Defaults to local timezone.")] = None,
        time_format: Annotated[str, Field(
            description="Format of the current time, optional. Defaults to %Y-%m-%d %H:%M:%S.")] = "%Y-%m-%d %H:%M:%S",
) -> GetCurrentTimeResult:
    """Raises:
        ValueError: If the timezone name is invalid, or if the format is invalid.
    """

    if timezone_name is not None and not isinstance(timezone_name, str):
        log.error("Timezone name must be a string")
        raise ToolError(message="Timezone name must be a string", code=400)

    if not isinstance(time_format, str):
        log.error("Format must be a string")
        raise ToolError(message="Format must be a string", code=400)

    from datetime import datetime
    import tzlocal

    local_tz = tzlocal.get_localzone()

    # If a timezone name is provided, and it is not the local timezone, convert the current time to that timezone
    if timezone_name:
        try:
            if local_tz is None:
                log.error("Local timezone is not available")
                raise ToolError(message="Local timezone is not available", code=400)

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

        except BaseException as e:
            import traceback
            log.error(f"Error getting current time in timezone '{timezone_name}': {e}:\n{traceback.format_exc()}")
            raise ToolError(message=f"Error getting current time in timezone '{timezone_name}': {e}", code=500)

    now = datetime.now(local_tz)
    local_utcoffset = now.utcoffset()

    return GetCurrentTimeResult(
        datetime=now.strftime(time_format),
        tz_name=str(local_tz) if local_tz else None,
        tz_offset=int(local_utcoffset.total_seconds()) if local_utcoffset else None
    )


get_unix_timestamp_tool_description: str = "Gets the current Unix timestamp as seconds since January 1, 1970 UTC (Epoch time)."
get_unix_timestamp_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {},
    "required": [],
}


def get_unix_timestamp() -> Annotated[
    int, Field(description="Current time Unix timestamp as seconds since January 1, 1970 UTC (Epoch time).")]:
    from datetime import datetime

    return int(datetime.now().timestamp())


get_system_info_tool_description: str = (
    "Gets system information, including system, node name, release, version, machine, processor, CPU count, "
    "memory total, and swap total.")
get_system_info_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {},
    "required": [],
}


# System information and status tools.

def get_system_info() -> dict:
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


get_system_stats_tool_description: str = (
    "Gets system stats, including boot time, CPU count, CPU percent, memory percent, memory total, memory used, "
    "memory free, swap percent, swap total, swap used and swap free.")
get_system_stats_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {},
    "required": [],
}


async def get_system_stats() -> dict:
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


read_lines_tool_description: str = (
    "Reads the lines of a file with a max bytes limit of 10MB."
    "Returns it as a list of strings in utf-8 encoding.")
read_lines_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "file_path": {
            "type": "string",
            "description": "File path to read lines, absolute or relative, required.",
        },
        "file_encoding": {
            "type": "string",
            "description": "File encoding to read lines, optional, defaults to utf-8.",
        },
        "working_directory": {
            "type": "string",
            "description": "Working directory to use for relative file paths, optional, defaults to current working directory.",
        },
        "begin_line": {
            "type": "integer",
            "description": "Beginning position to read from, optional, defaults to 1. Negative values indicate reading from the N to last line, e.g. -1 means last line, -2 means second to last line, etc.",
        },
        "max_lines": {
            "type": "integer",
            "description": "Maximum number of lines to read, optional, defaults to 200, max 10000.",
        },
    },
    "required": ["file_path"],
}
read_lines_tool_output_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "file_path": {
            "type": "string",
            "description": "File path to read lines, absolute or relative, required.",
        },
        "begin_line": {
            "type": "integer",
            "description": "Beginning position to read from, optional, defaults to 1. Negative values indicate reading from the N to last line, e.g. -1 means last line, -2 means second to last line, etc.",
        },
        "read_lines": {
            "type": "integer",
            "description": "Number of lines read from the file.",
        },
        "lines": {
            "type": "array",
            "description": "Content lines of the file as a list of strings in utf-8 encoding.",
        },
    },
    "required": ["file_path"],
}


# File system tools.

async def read_lines(
        file_path: Annotated[str, Field(description="File path to read lines, absolute or relative, required.")],
        file_encoding: Annotated[
            str, Field(description="File encoding to read lines, optional, defaults to utf-8.")] = "utf-8",
        working_directory: Annotated[
            str, Field(description="Working directory to use for relative file paths, optional, "
                                   "defaults to current working directory.")
        ] = os.getcwd(),
        begin_line: Annotated[
            int, Field(description="Beginning position to read from, optional, defaults to 1. "
                                   "Negative values indicate reading from the N to last line, e.g. -1 means last line, -2 means second to last line, etc.")] = 1,
        max_lines: Annotated[
            int,
            Field(description="Maximum number of lines to read, optional, defaults to 200, max 10000."),
        ] = 200,
) -> ReadLinesResult:
    """Note:
        In Python 3, str is Unicode. You should decode the file using the specified file_encoding and return the str.
        The transport/JSON layer will UTF‑8 encode it as needed.

    Raises:
        ValueError: If the file does not exist or is not readable.
    """

    lines = await do_read_lines(file_path=file_path, file_encoding=file_encoding,
                                working_directory=working_directory,
                                begin_line=begin_line, max_lines=max_lines,
                                strip_lf=True,
                                )
    file_path = os.path.expanduser(file_path.strip())
    file_path = os.path.join(working_directory, file_path) if not os.path.isabs(file_path) else file_path
    file_path = os.path.normpath(file_path).replace(os.sep, "/")

    return ReadLinesResult(file_path=file_path, begin_line=begin_line, num_lines=len(lines), content_lines=lines)


async def do_read_lines(file_path: str, file_encoding: str = "utf-8",
                        working_directory: str = os.getcwd(),
                        begin_line: int = 1, max_lines: int = 200,
                        strip_lf: bool = True,
                        ) -> list[str]:
    if not isinstance(file_path, str) or not file_path.strip():
        log.error(f"File path must be a non-empty string, but got '{file_path}'")
        raise ToolError(message="File path must be a non-empty string", code=400)
    if not isinstance(file_encoding, str) or not file_encoding.strip():
        log.error(f"File encoding must be a non-empty string, but got '{file_encoding}'")
        raise ToolError(message="File encoding must be a non-empty string", code=400)
    if not isinstance(working_directory, str) or not working_directory.strip():
        log.error(f"Working directory must be a non-empty string, but got '{working_directory}'")
        raise ToolError(message="Working directory must be a non-empty string", code=400)
    if not isinstance(begin_line, int) or begin_line == 0:
        log.error(f"Begin line must be a non-zero integer, but got '{begin_line}'")
        raise ToolError(message="Begin line must be a non-zero integer", code=400)
    if not isinstance(max_lines, int) or max_lines < 1 or max_lines > 10000:
        log.error(f"Max lines must be a positive integer between 1 and 10000, but got '{max_lines}'")
        raise ToolError(message="Max lines must be a positive integer between 1 and 10000", code=400)

    try:
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        file_path = os.path.expanduser(file_path.strip())
        file_path = os.path.join(working_directory, file_path) if not os.path.isabs(file_path) else file_path
        file_path = os.path.normpath(file_path).replace(os.sep, "/")

        if not os.path.exists(file_path):
            raise ToolError(message=f"File '{file_path}' does not exist or is not readable", code=404)

        file_size = os.path.getsize(file_path)
        log.debug(f"Reading file lines '{file_path}' with encoding '{file_encoding}', "
                  f"begin line {begin_line}, max lines {max_lines}, file size {file_size} bytes")

        with open(file_path, 'r', encoding=file_encoding) as f:
            if begin_line < 0:
                from collections import deque  # add near the other local imports in this branch

                k = abs(begin_line)
                window = deque(maxlen=k + max_lines)

                # Single pass: keep only the last k + max_lines lines
                for line in f:
                    window.append(line)

                # Compute slice within the window
                L = len(window)  # == min(total_lines, k + max_lines)
                start_idx = max(0, L - k)  # start of desired range in the window
                d = min(max_lines, k, L - start_idx)

                # Build result and enforce 10MB cap on returned content
                lines = []
                total_bytes = 0
                for line in list(window)[start_idx:start_idx + d]:
                    n_bytes = len(line.encode("utf-8"))
                    total_bytes += n_bytes
                    if total_bytes > max_size:
                        log.error("Content exceeds maximum size limit of 10MB")
                        raise ToolError(message="Content exceeds maximum size limit of 10MB", code=413)
                    lines.append(line if not strip_lf else line.rstrip("\r\n").rstrip("\n"))

            else:
                total_bytes = 0
                from itertools import islice
                lines = []
                for line in islice(f, begin_line - 1, begin_line - 1 + max_lines):
                    n_bytes = len(line.encode("utf-8"))
                    total_bytes += n_bytes
                    if total_bytes > max_size:
                        log.error("Content exceeds maximum size limit of 10MB")
                        raise ToolError(message="Content exceeds maximum size limit of 10MB", code=413)
                    lines.append(line if not strip_lf else line.rstrip("\r\n").rstrip("\n"))

            return lines

    except ToolError as e:
        raise e
    except BaseException as e:
        import traceback
        log.error(f"Error reading file '{file_path}': {e}\n{traceback.format_exc()}")
        raise ToolError(f"Error reading file '{file_path}': {e}", code=500)


read_files_tool_description: str = (
    "Reads all content of one or multiple files with a max size limit of 10MB per file."
    "Returns a content_list with the item of file_path and content in utf-8 encoding.")
read_files_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "file_paths": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": "File paths to read, absolute or relative, required.",
        },
        "file_encodings": {
            "type": "array",
            "items": {
                "type": ["string", "null"],
            },
            "description": "File encodings to read, optional, empty or None to use utf-8 encoding for each file.",
        },
        "skip_errors": {
            "type": "boolean",
            "description": "Whether to skip errors when reading files, optional, defaults to True.",
        },
        "working_directory": {
            "type": "string",
            "description": "Working directory to use for relative file paths, optional, defaults to current working directory.",
        },
    },
    "required": ["file_paths"],
}
read_files_tool_output_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "content_list": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file that was read.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content of the file, in utf-8 encoding.",
                    },
                },
                "required": ["file_path"],
            },
            "description": "Contents of the files that were read.",
        },
    },
    "required": [],
}


async def read_files(
        file_paths: Annotated[list[str], Field(description="File paths to read, absolute or relative, required.")],
        file_encodings: Annotated[
            list[str | None], Field(
                description="File encodings to read, optional, empty or None to use utf-8 encoding for each file.")
        ] = None,
        skip_errors: Annotated[
            bool, Field(description="Whether to skip errors when reading files, optional, defaults to True.")
        ] = True,
        working_directory: Annotated[
            str, Field(
                description="Working directory to use for relative file paths, optional, defaults to current working directory.")
        ] = os.getcwd(),
) -> ReadFilesResult:
    """Raises:
        ValueError: If any file does not exist or is not readable, or if the file encoding is invalid and skip_errors is False.
    """

    # Validate inputs
    if not isinstance(file_paths, list) or not file_paths:
        log.error("File paths must be a non-empty list of strings")
        raise ToolError(message="File paths must be a non-empty list of strings", code=400)
    if not isinstance(skip_errors, bool):
        log.error("skip_errors must be a boolean")
        raise ToolError(message="skip_errors must be a boolean", code=400)
    if not isinstance(working_directory, str) or not working_directory.strip():
        log.error("Working directory must be a non-empty string")
        raise ToolError(message="Working directory must be a non-empty string", code=400)

    # Normalize and validate each file path; keep original and resolved path
    normalized_paths: list[str] = []
    for p in file_paths:
        if not isinstance(p, str) or not p.strip():
            log.error(f"File path must be a non-empty string, but got '{p}'")
            raise ToolError(message="File paths must be a non-empty list of strings", code=400)
        p = p.strip()
        p = os.path.expanduser(p)
        p = os.path.join(working_directory, p) if not os.path.isabs(p) else p
        # Normalize, then force forward slashes on all OSes
        resolved = os.path.normpath(p).replace(os.sep, "/")
        normalized_paths.append(resolved)

    # Align encodings with paths; default to utf-8 when missing/empty
    encs: list[str | None]
    if not isinstance(file_encodings, list) or len(file_encodings) == 0:
        encs = [None] * len(file_paths)
    else:
        encs = []
        for i in range(len(file_paths)):
            enc = file_encodings[i] if i < len(file_encodings) else None
            if enc is not None and not isinstance(enc, str):
                if skip_errors:
                    log.warning(f"Invalid file encoding for '{file_paths[i]}', defaulting to utf-8")
                    enc = None
                else:
                    log.error(f"Invalid file encoding value for '{file_paths[i]}'")
                    raise ToolError(f"Invalid file encoding value for '{file_paths[i]}'", code=400)
            encs.append(enc)

    content_list: list[FileContent] = []
    max_size = 10 * 1024 * 1024  # 10MB in bytes

    for resolved_path, enc in zip(normalized_paths, encs):
        log.debug(f"Reading file '{resolved_path}' with encoding '{enc if enc else 'utf-8'}'...")

        try:
            if not os.path.exists(resolved_path) or not os.path.isfile(resolved_path):
                error_msg = f"File '{resolved_path}' does not exist or is not readable"
                if skip_errors:
                    log.warning(f"Skipping file '{resolved_path}': {error_msg}")
                    continue
                log.error(error_msg)
                raise ToolError(message=error_msg, code=404)

            file_size = os.path.getsize(resolved_path)
            if file_size > max_size:
                error_msg = f"File '{resolved_path}' exceeds maximum size limit of 10MB"
                if skip_errors:
                    log.warning(f"Skipping file '{resolved_path}': {error_msg}")
                    continue
                log.error(error_msg)
                raise ToolError(message=error_msg, code=413)

            encoding_to_use = 'utf-8' if enc is None or (isinstance(enc, str) and not enc.strip()) else enc.strip()

            with open(resolved_path, 'r', encoding=encoding_to_use) as f:
                content = f.read()

            content_list.append(FileContent(file_path=resolved_path, content=content))

        except ToolError as e:
            raise e
        except BaseException as e:
            import traceback
            if skip_errors:
                log.warning(f"Skipping file '{resolved_path}': {e}:\n{traceback.format_exc()}")
                continue
            log.error(f"Error reading file '{resolved_path}': {e}:\n{traceback.format_exc()}")
            raise ToolError(f"Error reading file '{resolved_path}': {e}", code=500)

    return ReadFilesResult(content_list=content_list)


check_connectivity_tool_description: str = (
    "Checks connectivity to a destination using curl command with optional timeout and proxy options. "
    "Returns a description of the connectivity status.")
check_connectivity_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "destination": {
            "type": "string",
            "description": "Destination to check connectivity to, required, can be a hostname, IP address, or URL.",
        },
        "timeout": {
            "type": "number",
            "description": "Timeout for the curl command in seconds, optional, defaults to 15 seconds.",
        },
        "proxy_enabled": {
            "type": "boolean",
            "description": "Whether to enable the proxy settings, optional, defaults to False.",
        },
        "proxy": {
            "type": ["string", "null"],
            "description": "Proxy server to use, optional, defaults to system proxy settings.",
        },
        "proxy_username": {
            "type": ["string", "null"],
            "description": "Username for the proxy server, optional, defaults to system proxy settings.",
        },
        "proxy_password": {
            "type": ["string", "null"],
            "description": "Password for the proxy server, optional, defaults to system proxy settings.",
        },
    },
    "required": ["destination"],
}


# Network tools.

async def check_connectivity(
        destination: Annotated[
            str,
            Field(description="Destination to check connectivity to, required, can be a hostname, IP address, or URL.")
        ],
        timeout: Annotated[
            float,
            Field(description="Timeout for the curl command in seconds, optional, defaults to 15 seconds.")
        ] = 15.0,
        proxy_enabled: Annotated[
            bool,
            Field(description="Whether to enable the proxy settings, optional, defaults to False.")
        ] = True,
        proxy: Annotated[
            str,
            Field(description="Proxy server to use, optional, defaults to system proxy settings.")
        ] = None,
        proxy_username: Annotated[
            str,
            Field(description="Username for the proxy server, optional, defaults to system proxy settings.")
        ] = None,
        proxy_password: Annotated[
            str,
            Field(description="Password for the proxy server, optional, defaults to system proxy settings.")
        ] = None,
) -> Annotated[str, Field(description="Description of the connectivity status.")]:
    """Raises:
        ValueError: If the destination is invalid.
    """

    if not destination or not isinstance(destination, str) or not destination.strip():
        log.error("Destination must be a non-empty DNS name or IP address")
        raise ToolError(message="Destination must be a non-empty DNS name or IP address", code=400)

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
        log.debug(f"Checking connectivity to {destination}: {' '.join(cmd)}...")

        completed = subprocess.run(
            cmd,
            timeout=timeout + 1.0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # decode bytes to str using locale encoding
            check=False
        )

        error = completed.stderr.strip() if completed.stderr else None
        if completed.returncode in (7, 28):
            log.error(f"Error checking connectivity to {destination} (code {completed.returncode}): "
                      f"{error if error else 'No error message'}")
            raise RuntimeError(f"Error checking connectivity to {destination} (code {completed.returncode}):\n"
                               f"{error if error else 'No error message'}")

        result = completed.stdout.strip() if completed.stdout else None

        return (
            f"Connectivity to {destination} is successful:\n"
            f"{result if result else 'No result from curl command'}"
            f"{'\n' + error if error else 'No error message'}"
        )

    except FileNotFoundError as e:
        log.error(f"Curl command not found on this system: {e}")
        raise FileNotFoundError(f"Curl command not found on this system: {e}")
    except TimeoutExpired as e:
        log.error(f"Connection to {destination} timed out after {timeout} seconds: {e}")
        raise TimeoutError(f"Connection to {destination} timed out after {timeout} seconds")


ping_tool_description: str = (
    "Pings a DNS name or IP address with the optional timeout and count. "
    "Returns details of the ping command."
)
ping_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "destination": {
            "type": "string",
            "description": "DNS name or IP address to ping, required.",
        },
        "timeout": {
            "type": "number",
            "description": "Timeout for the ping in seconds, optional, defaults to 15 seconds.",
        },
        "count": {
            "type": "integer",
            "description": "Number of pings to send, optional, defaults to 3.",
        },
    },
    "required": ["destination"],
}


async def ping(destination: Annotated[str, Field(description="DNS name or IP address to ping, required.")],
               timeout: Annotated[float, Field(description="Timeout for the ping in seconds, optional, "
                                                           "defaults to 15 seconds.")] = 15.0,
               count: Annotated[int, Field(description="Number of pings to send, optional, defaults to 3.")] = 3,
               ) -> Annotated[str, Field(description="Details of the ping command.")]:
    """Raises:
        ValueError: If the destination, timeout or count is invalid.
    """

    # Check destination
    if not destination or not isinstance(destination, str) or not destination.strip():
        log.error("Destination must be a non-empty DNS name or IP address")
        raise ToolError(message="Destination must be a non-empty DNS name or IP address", code=400)
    destination = destination.strip()
    # Check timeout
    if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 120:
        log.error("Timeout must be a positive number between 0 and 120 seconds")
        raise ToolError(message="Timeout must be a positive number between 0 and 120 seconds", code=400)
    # Check count
    if not isinstance(count, int) or count < 1 or count > 100:
        log.error("Count must be a positive integer between 1 and 100")
        raise ToolError(message="Count must be a positive integer between 1 and 100", code=400)

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
        log.debug(f"Pinging {destination}: {' '.join(cmd)}...")

        completed = subprocess.run(
            cmd,
            timeout=timeout + 1.0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # decode bytes to str using locale encoding
            check=False
        )

        # Check if the ping command was successful
        if completed.returncode != 0:
            log.error(f"Error pinging {destination} (code {completed.returncode}): "
                      f"{completed.stderr.strip() if completed.stderr else 'No error message'}")
            raise RuntimeError(f"Error pinging {destination} (code {completed.returncode}):\n"
                               f"{completed.stderr.strip() if completed.stderr else 'No error message'}")

        result = completed.stdout.strip() if completed.stdout else None
        if not result:
            log.error(f"No result from ping command for {destination}")
            raise RuntimeError(f"No result from ping command for {destination}")

        return result

    except FileNotFoundError as e:
        log.error(f"Ping command not found on this system: {e}")
        raise FileNotFoundError(f"Ping command not found on this system: {e}")
    except TimeoutExpired as e:
        log.error(f"Ping to {destination} timed out after {timeout} seconds: {e}")
        raise TimeoutError(f"Ping to {destination} timed out after {timeout} seconds")


evaluate_tool_description: str = (
    "Evaluates the given numeric expression with the given variables (if any). "
    "Returns numerical value of the expression."
)
evaluate_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "expression": {
            "type": "string",
            "description": "Numeric expression to evaluate, required.",
        },
        "variables": {
            "type": "object",
            "description": "Variables to use in the expression, if any, optional.",
        },
    },
    "required": ["expression"],
}


# Other tools.

def evaluate(
        expression: Annotated[str, Field(description="Numeric expression to evaluate, required.")],
        variables: Annotated[dict, Field(description="Variables to use in the expression, if any, optional.")] = None,
) -> Annotated[float, Field(description="Result of the evaluation.")]:
    """Raises:
        ValueError: If the expression is invalid, or if there are any issues with the evaluation.
    """

    if not isinstance(expression, str):
        log.error("Expression must be a string")
        raise ToolError(message="Expression must be a string", code=400)

    if variables is not None and not isinstance(variables, dict):
        log.error("Variables must be a dictionary")
        raise ToolError(message="Variables must be a dictionary", code=400)

    # Evaluate the expression using numexpr
    try:
        import numexpr as ne

        result = ne.evaluate(expression, local_dict=variables)
    except BaseException as e:
        import traceback
        log.error(f"Error evaluating expression '{expression}' with variables {variables}:\n{traceback.format_exc()}")
        raise ToolError(message=f"Error evaluating expression: {e}", code=400)

    return float(result)


generate_uuid_tool_description: str = (
    "Generates one or multiple UUIDs with the specified version, defaults to one UUID of version 4 (random). "
    "Returns a list of UUID strings."
)
generate_uuid_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "count": {
            "type": "integer",
            "description": "Number of UUIDs to generate, optional, defaults to 1.",
        },
        "version": {
            "type": "integer",
            "description": "UUID version (1, 3, 4, or 5), optional, defaults to 4 (random).",
        },
    },
    "required": [],
}
generate_uuid_tool_output_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "uuids": {
            "type": "array",
            "description": "List of generated UUID strings.",
        },
    },
    "required": ["uuids"],
}


def generate_uuid(
        count: Annotated[int, Field(description="Number of UUIDs to generate, optional, defaults to 1.")] = 1,
        version: Annotated[
            int, Field(description="UUID version (1, 3, 4, or 5), optional, defaults to 4 (random).")] = 4,
        namespace: Annotated[str, Field(description="Namespace UUID (required for versions 3 and 5). "
                                                    "Must be a valid UUID string or one of the predefined namespaces: 'dns', 'url', 'oid', 'x500'.")] = None,
        name: Annotated[str, Field(description="Name string (required for versions 3 and 5).")] = None,
) -> GenerateUUIDResult:
    """Raises:
        ValueError: If the count is not a positive integer or if the version is not 1, 3, 4, or 5 or if the namespace or name is not provided for versions 3 and 5.
    """

    if not isinstance(count, int) or count < 1 or count > 1000:
        log.error("Count must be a positive integer between 1 and 1000")
        raise ToolError(message="Count must be a positive integer between 1 and 1000", code=400)

    import uuid

    if not isinstance(version, int) or version not in [1, 3, 4, 5]:
        log.error("UUID version must be an integer of 1, 3, 4, or 5")
        raise ToolError(message="UUID version must be an integer of 1, 3, 4, or 5", code=400)

    if version in [3, 5]:
        if namespace is None or name is None:
            log.error(f"Version {version} requires both namespace and name parameters")
            raise ToolError(message=f"Version {version} requires both namespace and name parameters", code=400)
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
                log.error("Invalid namespace UUID string, must be a valid UUID string or one of the predefined "
                          "namespaces: 'dns', 'url', 'oid', 'x500'")
                raise ToolError(
                    message="Invalid namespace UUID string, must be a valid UUID string or one of the predefined "
                            "namespaces: 'dns', 'url', 'oid', 'x500'", code=400)
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
                log.error("UUID version must be 1, 3, 4, or 5")
                raise ToolError(message="UUID version must be 1, 3, 4, or 5", code=400)

        uuids.append(str(u))

    return GenerateUUIDResult(uuids=uuids)


sleep_tool_description: str = (
    "Sleeps for a specified amount of time. "
    "Time unit can be microseconds, milliseconds, seconds, minutes, hours, days or weeks, defaults to seconds."
)
sleep_tool_schema: dict[str, Any] = {
    "type": "object",
    "properties": {
        "time_value": {
            "type": "number",
            "description": "Time value to sleep for, in 'time_unit' units, required.",
        },
        "time_unit": {
            "type": "string",
            "description": "Time unit to sleep for, optional, defaults to seconds. "
                           "Can be microseconds, milliseconds, seconds, minutes, hours, days or weeks.",
        },
    },
    "required": ["time_value"],
}


async def sleep(
        time_value: Annotated[
            float,
            Field(description="Time value to sleep for, in 'time_unit' units, required.")
        ],
        time_unit: Annotated[
            str,
            Field(description="Time unit to sleep for, optional, defaults to seconds. "
                              "Can be microseconds, milliseconds, seconds, minutes, hours, days or weeks.")] = "seconds",
) -> Annotated[str, Field(description="A message indicating that the server has slept for the specified duration.")]:
    """Raises:
        ValueError: If time_value is not positive or if an invalid time unit is provided.
    """

    conversion_factors = {
        "microseconds": 0.000001,
        "milliseconds": 0.001,
        "seconds": 1,
        "minutes": 60,
        "hours": 3600,
        "days": 86400,
        "weeks": 604800,
    }

    if time_value <= 0:
        log.error("Sleep duration must be a positive number")
        raise ToolError(message="Sleep duration must be a positive number", code=400)

    if time_unit not in conversion_factors:
        valid_units = ", ".join(f'"{unit}"' for unit in conversion_factors.keys())
        log.error(f"Invalid time unit: {time_unit}. Please use one of: {valid_units}")
        raise ToolError(message=f"Invalid time unit. Please use one of: {valid_units}", code=400)

    sleep_duration_seconds = time_value * conversion_factors[time_unit]

    start_time = time.perf_counter()
    time.sleep(sleep_duration_seconds)
    end_time = time.perf_counter()
    elapsed = end_time - start_time

    sys.stderr.write(f"Actual sleep time: {elapsed:.6f} seconds.\n")
    return f"Server slept for {time_value} {time_unit}."
