import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utilities_box_mcp_server.tools import ping, check_connectivity


class TestPing(unittest.TestCase):
    def test_ping(self):
        result = asyncio.run(ping(destination="baidu.com"))
        print(result)

    def test_check_connectivity(self):
        result = asyncio.run(check_connectivity(destination="1.1.1.1"))
        print(result)
