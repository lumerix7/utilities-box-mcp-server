import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utilities_box_mcp_server import main as main_server


def main():
    os.environ["SIMP_LOGGER_LOG_LEVEL"] = "DEBUG"
    os.environ["SIMP_LOGGER_LOG_CONSOLE_ENABLED"] = "False"
    os.environ["UTILITIES_BOX_TRANSPORT"] = "stdio"

    main_server()


if __name__ == "__main__":
    main()
