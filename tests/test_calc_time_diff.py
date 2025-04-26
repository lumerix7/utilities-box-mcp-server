import os
import sys
import unittest

# Insert src root directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from utilities_box_mcp_server.server import calc_time_diff


class TestCalcTimeDiff(unittest.TestCase):
    def test_calc_time_diff(self):
        # Test with two datetime strings in the same timezone
        datetime1 = "2023-10-01 12:00:00"
        datetime2 = "2023-10-01 14:00:00"
        result = calc_time_diff(datetime1, datetime2)
        print(result)
        self.assertEqual(result, 7200)  # 2 hours in seconds

        result = calc_time_diff(start_time=datetime1, end_time=datetime2, diff_unit="microseconds")
        print(result)
        self.assertEqual(result, 7200_000_000)

        result = calc_time_diff(start_time=datetime1, end_time=datetime2, diff_unit="milliseconds")
        print(result)
        self.assertEqual(result, 7200_000)

        result = calc_time_diff(start_time=datetime1, end_time=datetime2, diff_unit="seconds")
        print(result)
        self.assertEqual(result, 7200)

        result = calc_time_diff(start_time=datetime1, end_time=datetime2, diff_unit="minutes")
        print(result)
        self.assertEqual(result, 120)

        result = calc_time_diff(start_time=datetime1, end_time=datetime2, diff_unit="hours")
        print(result)
        self.assertEqual(result, 2)

        result = calc_time_diff(start_time=datetime1, end_time=datetime2, diff_unit="days")
        print(result)
        self.assertEqual(result, 2 / 24)

        result = calc_time_diff(start_time=datetime1, end_time=datetime2, diff_unit="weeks")
        print(result)
        self.assertEqual(result, 2 / 168)

    def test_calc_time_diff_different_timezones(self):
        # Test with two datetime strings in different timezones
        datetime1 = "2023-10-01T12:00:00+0000"
        datetime2 = "2023-10-01T14:00:00+0200"
        result = calc_time_diff(start_time=datetime1, end_time=datetime2, time_format="%Y-%m-%dT%H:%M:%S%z")
        print(result)
        self.assertEqual(result, 0)

        datetime1 = "2023-10-01T12:00:00+0000"
        datetime2 = "2023-10-01T12:00:00+0200"
        result = calc_time_diff(start_time=datetime1, end_time=datetime2, time_format="%Y-%m-%dT%H:%M:%S%z")
        print(result)
        self.assertEqual(result, -7200)

    def test_calc_time_diff_invalid_format(self):
        # Test with an invalid datetime format
        with self.assertRaises(ValueError):
            calc_time_diff("invalid_datetime", "2023-10-01 14:00:00")
