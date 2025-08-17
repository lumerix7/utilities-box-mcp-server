import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utilities_box_mcp_server.tools import generate_uuid
from src.utilities_box_mcp_server.schema import GenerateUUIDResult


class TestGenerateUUID(unittest.TestCase):
    def test_generate_uuid(self):
        result = generate_uuid()
        self.assertIsInstance(result, GenerateUUIDResult)
        self.assertIsInstance(result.uuids, list)

        uuids = result.uuids
        self.assertEqual(len(uuids), 1)
        for uuid in uuids:
            print(uuid)
            self.assertIsInstance(uuid, str)
            self.assertEqual(len(uuid), 36)

    def test_generate_multiple_uuids(self):
        result = generate_uuid(count=5)
        self.assertIsInstance(result, GenerateUUIDResult)
        self.assertIsInstance(result.uuids, list)

        uuids = result.uuids
        self.assertEqual(len(uuids), 5)
        for uuid in uuids:
            print(uuid)
            self.assertIsInstance(uuid, str)
            self.assertEqual(len(uuid), 36)

    def test_generate_uuid_with_invalid_count(self):
        with self.assertRaises(ValueError):
            generate_uuid(count=0)
        with self.assertRaises(ValueError):
            generate_uuid(count=-1)
        with self.assertRaises(ValueError):
            generate_uuid(count="invalid")

    def test_generate_version_1_uuid(self):
        result = generate_uuid(version=1)
        self.assertIsInstance(result, GenerateUUIDResult)
        self.assertIsInstance(result.uuids, list)

        uuids = result.uuids
        self.assertEqual(len(uuids), 1)
        for uuid in uuids:
            print(uuid)
            self.assertIsInstance(uuid, str)
            self.assertEqual(len(uuid), 36)

    def test_generate_version_3_uuid(self):
        result = generate_uuid(version=3, namespace="3bc6ea4b-b999-4ac1-8d6d-99565301495f", name="example_name")
        self.assertIsInstance(result, GenerateUUIDResult)
        self.assertIsInstance(result.uuids, list)

        uuids = result.uuids
        self.assertEqual(len(uuids), 1)
        for uuid in uuids:
            print(uuid)
            self.assertIsInstance(uuid, str)
            self.assertEqual(len(uuid), 36)

        result = generate_uuid(version=3, namespace="3bc6ea4b-b999-4ac1-8d6d-99565301495f", name="")
        self.assertIsInstance(result, GenerateUUIDResult)
        self.assertIsInstance(result.uuids, list)

        uuids = result.uuids
        self.assertEqual(len(uuids), 1)
        for uuid in uuids:
            print(uuid)
            self.assertIsInstance(uuid, str)
            self.assertEqual(len(uuid), 36)

        result = generate_uuid(count=3, version=3, namespace="dns", name="name3")
        self.assertIsInstance(result, GenerateUUIDResult)
        self.assertIsInstance(result.uuids, list)

        uuids = result.uuids
        self.assertEqual(len(uuids), 3)
        for uuid in uuids:
            print(uuid)
            self.assertIsInstance(uuid, str)
            self.assertEqual(len(uuid), 36)
            # Check that each UUID appears exactly once in the list (verifies uniqueness)
            self.assertEqual(1, uuids.count(uuid))

    def test_generate_version_4_uuid(self):
        result = generate_uuid(version=4)
        self.assertIsInstance(result, GenerateUUIDResult)
        self.assertIsInstance(result.uuids, list)

        uuids = result.uuids
        self.assertEqual(len(uuids), 1)
        for uuid in uuids:
            print(uuid)
            self.assertIsInstance(uuid, str)
            self.assertEqual(len(uuid), 36)

    def test_generate_version_5_uuid(self):
        result = generate_uuid(count=5, version=5, namespace="3bc6ea4b-b999-4ac1-8d6d-99565301495f",
                               name="example_name")

        self.assertIsInstance(result, GenerateUUIDResult)
        self.assertIsInstance(result.uuids, list)

        uuids = result.uuids
        self.assertEqual(len(uuids), 5)
        for uuid in uuids:
            print(uuid)
            self.assertIsInstance(uuid, str)
            self.assertEqual(len(uuid), 36)
            # Check that each UUID appears exactly once in the list (verifies uniqueness)
            self.assertEqual(1, uuids.count(uuid))
