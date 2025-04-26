import asyncio
import os
import sys
import unittest

# Insert src root directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from utilities_box_mcp_server.server import get_system_stats


class TestGetSystemInfo(unittest.TestCase):
    def test_get_system_info(self):
        # Call the function to retrieve system stats
        result = asyncio.run(get_system_stats())
        print(result)

        # Check if the result is a dictionary
        self.assertIsInstance(result, dict)

        # Check if the dictionary contains expected keys
        expected_keys = ["boot_time", "cpu_count", "cpu_percent", "memory_percent", "memory_total", "memory_used",
                         "memory_free", "swap_total", "swap_used", "swap_free", ]
        for key in expected_keys:
            self.assertIn(key, result)
            print(f"Key '{key}' found in result: {result[key]}")
