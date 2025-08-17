import asyncio
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utilities_box_mcp_server.tools import do_read_lines


class TestDoReadLinesNegative(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.test_dir.name, "test_file.txt")
        self.test_content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"

        # Create test file
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(self.test_content)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        self.test_dir.cleanup()

    def test_do_read_lines_with_negative_begin_line(self):
        """Test reading file starting from specific line from the end."""
        # -1 should read the last line
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=-1))
        expected = ["Line 5"]
        self.assertEqual(result, expected)

        # -2 should read from the second to last line
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=-2))
        expected = ["Line 4", "Line 5"]
        self.assertEqual(expected, result)

        # -3 should read from the third to last line
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=-3, max_lines=2))
        expected = ["Line 3", "Line 4"]
        self.assertEqual(expected, result)

        # -5 should read from the first line (all lines)
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=-5))
        self.assertEqual(self.test_content.split("\n")[:-1], result)

        # -10 should read from the first line (all lines) as it's beyond the file size
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=-10))
        self.assertEqual(self.test_content.split("\n")[:-1], result)

    def test_do_read_lines_with_negative_begin_line_and_max_lines(self):
        """Test reading file with negative begin line and max lines."""
        # -2 with max_lines=1 should read only the fourth line
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=-2, max_lines=1))
        expected = ["Line 4"]
        self.assertEqual(expected, result)

        # -3 with max_lines=2 should read the third and fourth lines
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=-3, max_lines=2))
        expected = ["Line 3", "Line 4"]
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
