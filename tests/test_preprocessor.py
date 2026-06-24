import unittest
from src.preprocessor import preprocess

class TestPreprocessor(unittest.TestCase):
    def test_single_strip(self):
        source = (
            "#editor-note 2 , :\n"
            "quest ( Frodo equal Sam, oops! such a thing would never happen, silly writer: ) {\n"
            "}"
        )
        result = preprocess(source)
        lines = result.splitlines()
        
        # Verify length is preserved
        self.assertEqual(len(lines), 3)
        self.assertEqual(len(lines[0]), len("#editor-note 2 , :"))
        self.assertEqual(len(lines[1]), len("quest ( Frodo equal Sam, oops! such a thing would never happen, silly writer: ) {"))
        
        # Verify directive line is whitespace
        self.assertTrue(lines[0].isspace())
        
        # Verify the zone is stripped with spaces
        self.assertIn("quest ( Frodo equal Sam ", lines[1])
        self.assertIn(" ) {", lines[1])
        # The segment ', oops! ... :' should be replaced by spaces
        self.assertNotIn("oops!", lines[1])

    def test_multiple_directives(self):
        source = (
            "#editor-note 3 , :\n"
            "#editor-note 4 [ ]\n"
            "quest ( Frodo equal Sam, oops! : ) {\n"
            "  hobbit myVar is [ignore me] 10 .\n"
            "}"
        )
        result = preprocess(source)
        lines = result.splitlines()
        
        self.assertEqual(len(lines), 5)
        self.assertTrue(lines[0].isspace())
        self.assertTrue(lines[1].isspace())
        
        self.assertNotIn("oops!", lines[2])
        self.assertNotIn("ignore me", lines[3])
        
        # Ensure lengths match
        orig_lines = source.splitlines()
        for orig, res in zip(orig_lines, lines):
            self.assertEqual(len(orig), len(res))

if __name__ == '__main__':
    unittest.main()
