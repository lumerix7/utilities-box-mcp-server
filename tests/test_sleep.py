import asyncio
import os
import sys
import unittest

# Insert src root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src")

from utilities_box_mcp_server.server import sleep


class TestSleep(unittest.TestCase):
    def test_sleep_default_unit(self):
        result = asyncio.run(sleep(time_value=0.5))
        print(result)
        self.assertIsInstance(result, str)

    def test_sleep_with_unit(self):
        result = asyncio.run(sleep(time_value=500, time_unit="milliseconds"))
        print(result)
        self.assertIsInstance(result, str)

        result = asyncio.run(sleep(time_value=500, time_unit="microseconds"))
        print(result)
        self.assertIsInstance(result, str)

        result = asyncio.run(sleep(time_value=0.05, time_unit="seconds"))
        print(result)
        self.assertIsInstance(result, str)

        result = asyncio.run(sleep(time_value=0.005, time_unit="minutes"))
        print(result)
        self.assertIsInstance(result, str)

        result = asyncio.run(sleep(time_value=0.0005, time_unit="hours"))
        print(result)
        self.assertIsInstance(result, str)

        result = asyncio.run(sleep(time_value=0.00005, time_unit="days"))
        print(result)
        self.assertIsInstance(result, str)

        result = asyncio.run(sleep(time_value=0.000005, time_unit="weeks"))
        print(result)
        self.assertIsInstance(result, str)

    def test_sleep_negative_value(self):
        with self.assertRaises(ValueError):
            asyncio.run(sleep(time_value=-1))

    def test_sleep_invalid_unit(self):
        with self.assertRaises(ValueError):
            asyncio.run(sleep(time_value=1, time_unit="invalid_unit"))
