import asyncio
import os
import sys
import unittest

# Insert src root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src")

from utilities_box_mcp_server.server import ping, check_connectivity


class TestPing(unittest.TestCase):
    def test_ping(self):
        result = asyncio.run(ping(destination="baidu.com"))
        print(result)

    def test_check_connectivity(self):
        result = asyncio.run(check_connectivity(destination="1.1.1.1"))
        print(result)
