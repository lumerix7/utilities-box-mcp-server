import os
import sys
import unittest
from datetime import datetime

import tzlocal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utilities_box_mcp_server.tools import get_current_time
from src.utilities_box_mcp_server.schema import GetCurrentTimeResult


class TestGetCurrentTime(unittest.TestCase):
    def test_get_current_time_default(self):
        local_tz = tzlocal.get_localzone()
        now = datetime.now(local_tz)
        local_utcoffset = now.utcoffset().total_seconds()

        result = get_current_time()
        print(result)

        self.assertIsInstance(result, GetCurrentTimeResult)
        self.assertRegex(result.datetime, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
        self.assertEqual(result.tz_name, str(local_tz))
        self.assertIsInstance(result.tz_offset, int)
        self.assertEqual(result.tz_offset, local_utcoffset)

    def test_get_current_time_with_same_timezone(self):
        local_tz = tzlocal.get_localzone()
        now = datetime.now(local_tz)
        local_utcoffset = now.utcoffset().total_seconds()

        result = get_current_time(timezone_name=str(local_tz), time_format="%Y-%m-%dT%H:%M:%S%z")
        print(result)

        self.assertIsInstance(result, GetCurrentTimeResult)
        self.assertRegex(result.datetime, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{4}$")
        self.assertEqual(result.tz_name, str(local_tz))
        self.assertIsInstance(result.tz_offset, int)
        self.assertEqual(result.tz_offset, local_utcoffset)

    def test_get_current_time_with_different_timezone(self):
        # Test with a different timezone
        result = get_current_time(timezone_name="America/New_York", time_format="%Y-%m-%dT%H:%M:%S%z")
        print(result)
        self.assertIsInstance(result, GetCurrentTimeResult)
        self.assertRegex(result.datetime, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{4}$")

    def test_get_current_time_with_invalid_timezone(self):
        # Test with an invalid timezone
        with self.assertRaises(ValueError):
            get_current_time("Invalid/Timezone")

    def test_get_current_time_with_format(self):
        # Test with a custom format
        result = get_current_time(time_format="%Y-%m-%d %H:%M:%S")
        print(result)
        self.assertIsInstance(result, GetCurrentTimeResult)
        self.assertRegex(result.datetime, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_get_current_time_with_invalid_format(self):
        # Test with an invalid format
        with self.assertRaises(ValueError):
            get_current_time(time_format=12345)
