import unittest
import os
from src.compiler import compile_clotr

class TestCompilerE2E(unittest.TestCase):
    def test_complete_program_compilation(self):
        program = (
            "#editor-note 3 , :\n"
            "hobbit Frodo is 0 .\n"
            "dwarf Sam is 1.5, oh lovely Sam: .\n"
            "elf Gandalf is 'G' .\n"
            "seek (Frodo less 5) {\n"
            "  Frodo is Frodo plus 1 .\n"
            "  quest (Sam greater_or_equal 3.0) {\n"
            "    Sam is Sam minus 1.0 .\n"
            "  } fulfilled unless {\n"
            "    Sam is Sam plus 0.5 .\n"
            "  }\n"
            "}"
        )
        
        # This should compile without raising any exceptions
        sam_code = compile_clotr(program)
        
        # Verify the structure of the output assembly code
        self.assertTrue(sam_code.startswith("ADDSP 3"))
        self.assertIn("PUSHIMM 0", sam_code)
        self.assertIn("STOREOFF 0", sam_code)
        
        # PUSHIMMF 1.5 instead of whole comment
        self.assertIn("PUSHIMMF 1.5", sam_code)
        self.assertNotIn("lovely", sam_code)
        
        # Ghent/Gandalf pushes character
        self.assertIn("PUSHIMMCH G", sam_code)
        self.assertIn("STOREOFF 2", sam_code)
        
        # Labels are generated for seek and quest
        self.assertIn("seek_start_", sam_code)
        self.assertIn("seek_end_", sam_code)
        self.assertIn("else_", sam_code)
        self.assertIn("end_quest_", sam_code)
        
        # Correctly terminates program
        self.assertIn("ADDSP -3", sam_code)
        self.assertIn("STOP", sam_code)

if __name__ == '__main__':
    unittest.main()
