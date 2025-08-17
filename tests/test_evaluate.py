import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utilities_box_mcp_server.tools import evaluate


class TestEvaluate(unittest.TestCase):
    def test_evaluate_simple(self):
        result = evaluate("2 + 2")
        print(result)
        self.assertEqual(result, 4)

    def test_evaluate_with_variables(self):
        result = evaluate("x + y", variables={"x": 2, "y": 3})
        print(result)
        self.assertEqual(result, 5)

    def test_evaluate_with_invalid_expression(self):
        with self.assertRaises(ValueError):
            evaluate("2 +")

    def test_evaluate_with_invalid_variables(self):
        with self.assertRaises(ValueError):
            evaluate("x + y", variables="invalid")

    def test_evaluate_with_missing_variables2(self):
        with self.assertRaises(ValueError):
            evaluate("x + y", variables={"x": 2})

    def test_evaluate_with_function(self):
        result = evaluate("sin(x)", variables={"x": 0})
        print(result)
        self.assertEqual(result, 0)
