import asyncio
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utilities_box_mcp_server.tools import read_files
from src.utilities_box_mcp_server.schema import ReadFilesResult, FileContent
from src.utilities_box_mcp_server.schema.exceptions import ToolError


def _norm(p: str) -> str:
    return os.path.normpath(p).replace(os.sep, "/")


class TestReadFiles(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.dir = self.test_dir.name

        # File 1: utf-8 content with multiple lines
        self.file1_path = os.path.join(self.dir, "file1.txt")
        self.file1_content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
        with open(self.file1_path, "w", encoding="utf-8") as f:
            f.write(self.file1_content)

        # File 2: latin-1 content
        self.file2_path = os.path.join(self.dir, "file2_latin1.txt")
        self.file2_content = "Café résumé naïve\n"
        with open(self.file2_path, "w", encoding="latin-1") as f:
            f.write(self.file2_content)

        # File 3: empty file
        self.file3_path = os.path.join(self.dir, "empty.txt")
        with open(self.file3_path, "w", encoding="utf-8") as f:
            pass

    def tearDown(self):
        self.test_dir.cleanup()

    def test_read_files_basic_absolute(self):
        # Absolute paths; default encodings
        result = asyncio.run(read_files([self.file1_path, self.file3_path]))
        expect = ReadFilesResult(
            content_list=[FileContent(file_path=_norm(self.file1_path), content=self.file1_content),
                          FileContent(file_path=_norm(self.file3_path), content="")])
        self.assertEqual(expect, result)

    def test_read_files_relative_with_working_directory(self):
        rel1 = os.path.basename(self.file1_path)
        rel3 = os.path.basename(self.file3_path)
        result = asyncio.run(read_files([rel1, rel3], working_directory=self.dir))
        expect = ReadFilesResult(
            content_list=[FileContent(file_path=_norm(self.file1_path), content=self.file1_content),
                          FileContent(file_path=_norm(self.file3_path), content="")])
        self.assertEqual(expect, result)

    def test_read_files_with_encodings(self):
        # Provide encodings list shorter than paths (default utf-8 for missing)
        result = asyncio.run(
            read_files(
                [self.file1_path, self.file2_path],
                file_encodings=[None, "latin-1"],
            )
        )
        expect = ReadFilesResult(
            content_list=[FileContent(file_path=_norm(self.file1_path), content=self.file1_content),
                          FileContent(file_path=_norm(self.file2_path), content=self.file2_content)])
        self.assertEqual(expect, result)

        # Blank encoding string should default to utf-8
        result2 = asyncio.run(
            read_files(
                [self.file1_path],
                file_encodings=[""],
            )
        )
        expect2 = ReadFilesResult(
            content_list=[FileContent(file_path=_norm(self.file1_path), content=self.file1_content)])
        self.assertEqual(expect2, result2)

    def test_read_files_invalid_encoding_value(self):
        # When skip_errors=True, invalid encoding type defaults to utf-8 and proceeds
        result = asyncio.run(
            read_files(
                [self.file1_path],
                file_encodings=[123],  # invalid type
                skip_errors=True,
            )
        )
        expect = ReadFilesResult(
            content_list=[FileContent(file_path=_norm(self.file1_path), content=self.file1_content)])
        self.assertEqual(expect, result)

        # When skip_errors=False, it should raise
        with self.assertRaises(ToolError):
            asyncio.run(
                read_files(
                    [self.file1_path],
                    file_encodings=[123],
                    skip_errors=False,
                )
            )

    def test_read_files_skip_errors_omits_failures(self):
        missing = os.path.join(self.dir, "does_not_exist.txt")
        result = asyncio.run(read_files([self.file1_path, missing], skip_errors=True))
        expect = ReadFilesResult(
            content_list=[FileContent(file_path=_norm(self.file1_path), content=self.file1_content)])
        self.assertEqual(expect, result)

    def test_read_files_skip_errors_false_raises_on_missing(self):
        missing = os.path.join(self.dir, "does_not_exist.txt")
        with self.assertRaises(ToolError):
            asyncio.run(read_files([self.file1_path, missing], skip_errors=False))

    def test_read_files_large_file_handling(self):
        # Create a file exceeding 10MB
        too_large_path = os.path.join(self.dir, "too_large.txt")
        with open(too_large_path, "w", encoding="utf-8") as f:
            f.write("X" * (11 * 1024 * 1024))

        # With skip_errors=True, it should be omitted while others succeed
        result = asyncio.run(read_files([self.file1_path, too_large_path], skip_errors=True))
        expect = ReadFilesResult(
            content_list=[FileContent(file_path=_norm(self.file1_path), content=self.file1_content)])
        self.assertEqual(expect, result)

        # With skip_errors=False, it should raise
        with self.assertRaises(ToolError):
            asyncio.run(read_files([self.file1_path, too_large_path], skip_errors=False))

    def test_read_files_invalid_parameters(self):
        # Empty file_paths
        with self.assertRaises(ToolError):
            asyncio.run(read_files([]))


if __name__ == "__main__":
    unittest.main()
