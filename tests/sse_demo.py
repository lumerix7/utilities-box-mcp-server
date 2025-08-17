import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utilities_box_mcp_server import main as main_server


def main():
    os.environ["SIMP_LOGGER_LOG_LEVEL"] = "DEBUG"
    os.environ["UTILITIES_BOX_SSE_PORT"] = "41104"
    os.environ["UTILITIES_BOX_TRANSPORT"] = "sse"

    main_server()


if __name__ == "__main__":
    main()
