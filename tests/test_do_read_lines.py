import asyncio
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utilities_box_mcp_server.tools import do_read_lines
from src.utilities_box_mcp_server.schema.exceptions import ToolError


class TestDoReadLines(unittest.TestCase):
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

    def test_do_read_lines_basic(self):
        """Test basic file reading functionality."""
        result = asyncio.run(do_read_lines(self.test_file_path))
        self.assertEqual(self.test_content.split("\n")[:-1], result)

    def test_do_read_lines_with_encoding(self):
        """Test file reading with specific encoding."""
        result = asyncio.run(do_read_lines(self.test_file_path, file_encoding='utf-8'))
        self.assertEqual(self.test_content.split("\n")[:-1], result)

    def test_do_read_lines_relative_path(self):
        """Test reading file with relative path."""
        relative_path = os.path.basename(self.test_file_path)
        result = asyncio.run(do_read_lines(
            relative_path,
            working_directory=self.test_dir.name
        ))
        self.assertEqual(self.test_content.split("\n")[:-1], result)

    def test_do_read_lines_with_begin_line(self):
        """Test reading file starting from specific line."""
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=2))
        expected = ["Line 2", "Line 3", "Line 4", "Line 5"]
        self.assertEqual(expected, result)

    def test_do_read_lines_with_max_lines(self):
        """Test reading file with maximum lines limit."""
        result = asyncio.run(do_read_lines(self.test_file_path, max_lines=2))
        expected = ["Line 1", "Line 2"]
        self.assertEqual(expected, result)

    def test_do_read_lines_with_begin_line_and_max_lines(self):
        """Test reading file with both begin line and max lines."""
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=2, max_lines=2))
        expected = ["Line 2", "Line 3"]
        self.assertEqual(expected, result)

    def test_do_read_lines_empty_file(self):
        """Test reading empty file."""
        empty_file = os.path.join(self.test_dir.name, "empty.txt")
        with open(empty_file, 'w') as f:
            pass

        result = asyncio.run(do_read_lines(empty_file))
        self.assertEqual([], result)

    def test_do_read_lines_nonexistent_file(self):
        """Test reading non-existent file raises ToolError."""
        nonexistent_file = os.path.join(self.test_dir.name, "nonexistent.txt")

        with self.assertRaises(ToolError) as cm:
            asyncio.run(do_read_lines(nonexistent_file))

        self.assertIn("does not exist", str(cm.exception))

    def test_do_read_lines_invalid_encoding(self):
        """Test reading file with invalid encoding."""
        # Create a file with invalid UTF-8 bytes
        invalid_utf8_file = os.path.join(self.test_dir.name, "invalid_utf8.txt")
        with open(invalid_utf8_file, 'wb') as f:
            # Write invalid UTF-8 sequence
            f.write(b'\xff\xfe\x00\x00invalid utf-8')

        with self.assertRaises(ToolError) as cm:
            asyncio.run(do_read_lines(invalid_utf8_file, file_encoding='utf-8'))

        self.assertIn("decode", str(cm.exception).lower())

    def test_do_read_lines_large_file(self):
        """Test reading large file (but under 10MB limit)."""
        large_file = os.path.join(self.test_dir.name, "large.txt")
        large_content = "Large file content\n" * 1000

        with open(large_file, 'w', encoding='utf-8') as f:
            f.write(large_content)

        result = asyncio.run(do_read_lines(large_file, max_lines=10000, strip_lf=True))
        self.maxDiff = None
        self.assertEqual(large_content.split("\n")[:-1], result)

    def test_do_read_lines_exceeds_size_limit(self):
        """Test that files exceeding 10MB limit raise ToolError."""
        # Create a file that exceeds 10MB
        large_file = os.path.join(self.test_dir.name, "too_large.txt")
        large_content = "X" * (11 * 1024 * 1024)  # 11MB

        with open(large_file, 'w', encoding='utf-8') as f:
            f.write(large_content)

        with self.assertRaises(ToolError) as cm:
            asyncio.run(do_read_lines(large_file))

        self.assertIn("exceeds maximum size limit", str(cm.exception))

    def test_do_read_lines_invalid_parameters(self):
        """Test parameter validation."""
        # Test empty file path
        with self.assertRaises(ToolError):
            asyncio.run(do_read_lines(""))

        # Test invalid begin_line
        with self.assertRaises(ToolError):
            asyncio.run(do_read_lines(self.test_file_path, begin_line=0))

        # Test invalid max_lines
        with self.assertRaises(ToolError):
            asyncio.run(do_read_lines(self.test_file_path, max_lines=0))

        with self.assertRaises(ToolError):
            asyncio.run(do_read_lines(self.test_file_path, max_lines=15000))

    def test_do_read_lines_unicode_content(self):
        """Test reading file with unicode content."""
        unicode_file = os.path.join(self.test_dir.name, "unicode.txt")
        unicode_content = "Hello 世界 🌍\nCafé\n"

        with open(unicode_file, 'w', encoding='utf-8') as f:
            f.write(unicode_content)

        result = asyncio.run(do_read_lines(unicode_file, file_encoding='utf-8'))
        self.assertEqual(unicode_content.split("\n")[:-1], result)

    def test_do_read_lines_with_different_encodings(self):
        """Test reading file with different encodings."""
        # Test with latin-1 encoding
        latin_file = os.path.join(self.test_dir.name, "latin.txt")
        latin_content = "Café résumé naïve\n"

        with open(latin_file, 'w', encoding='latin-1') as f:
            f.write(latin_content)

        result = asyncio.run(do_read_lines(latin_file, file_encoding='latin-1'))
        self.assertEqual(latin_content.split("\n")[:-1], result)

    def test_do_read_lines_single_line(self):
        """Test reading single line from file."""
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=3, max_lines=1))
        expected = ["Line 3"]
        self.assertEqual(expected, result)

    def test_do_read_lines_begin_line_beyond_end(self):
        """Test reading when begin_line is beyond file end."""
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=10))
        self.assertEqual([], result)

    def test_do_read_lines_max_lines_beyond_end(self):
        """Test when max_lines exceeds available lines."""
        result = asyncio.run(do_read_lines(self.test_file_path, begin_line=3, max_lines=10))
        expected = ["Line 3", "Line 4", "Line 5"]
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
