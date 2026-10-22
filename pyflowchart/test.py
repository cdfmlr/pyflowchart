import os
import tempfile
import unittest

from pyflowchart import flowchart_html


class DecoratorFlowchartTestCase(unittest.TestCase):
    def test_flowchart_decorator_writes_html(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "decorated_flowchart.html")

            @flowchart_html(output_file)
            def sample(value):
                if value > 0:
                    return "positive"
                return "non-positive"

            result = sample(3)

            self.assertEqual(result, "positive")
            self.assertTrue(os.path.exists(output_file))

            with open(output_file, "r", encoding="utf-8") as fh:
                content = fh.read()

            self.assertIn("flowchart.js", content)
            self.assertIn("sample", content)
            self.assertIn("if (value > 0)", content)


if __name__ == '__main__':
    unittest.main()
