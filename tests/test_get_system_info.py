import os
import sys
import unittest

# Insert src root directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from utilities_box_mcp_server.server import get_system_info


class TestGetSystemInfo(unittest.TestCase):
    def test_get_system_info(self):
        # Call the function to get system information
        result = get_system_info()
        print(result)

        # Check if the result is a dictionary
        self.assertIsInstance(result, dict)

        # Check if the dictionary contains expected keys
        expected_keys = ["system", "node_name", "release", "version", "machine", "processor", "cpu_count",
                         "memory_total", "swap_total", ]
        for key in expected_keys:
            self.assertIn(key, result)
            print(f"Key '{key}' found in result: {result[key]}")
