import os
import sys
import unittest

# Insert src root directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from utilities_box_mcp_server.server import get_unix_timestamp


class TestGetUnixTimestamp(unittest.TestCase):
    def test_get_unix_timestamp(self):
        # Test the get_unix_timestamp function
        result = get_unix_timestamp()
        print(result)

        # Check if the result is an integer
        self.assertIsInstance(result, int)

        # Check if the result is a positive integer
        self.assertGreaterEqual(result, 0)
