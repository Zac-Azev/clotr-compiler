import unittest
from src.lexer import tokenize
from src.parser import Parser
from src.generator import CodeGenerator, SemanticError

class TestGenerator(unittest.TestCase):
    def test_simple_arithmetic(self):
        source = "hobbit x is 5 plus 10 ."
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        gen = CodeGenerator(ast)
        code = gen.generate()
        
        # Check standard layout
        self.assertIn("ADDSP 1", code)
        self.assertIn("PUSHIMM 5", code)
        self.assertIn("PUSHIMM 10", code)
        self.assertIn("ADD", code)
        self.assertIn("STOREOFF 0", code)
        self.assertIn("ADDSP -1", code)
        self.assertIn("PUSHIMM 0", code)
        self.assertIn("STOP", code)

    def test_implicit_casting_itof(self):
        # x is float, y is int. Adding them should cast y to float.
        source = (
            "dwarf x is 5.5 .\n"
            "hobbit y is 10 .\n"
            "dwarf z is x plus y ."
        )
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        gen = CodeGenerator(ast)
        code = gen.generate()
        
        # Check that we declare 3 variables
        self.assertIn("ADDSP 3", code)
        
        # For 'z is x plus y':
        # x is loaded: PUSHOFF 0
        # y is loaded: PUSHOFF 1
        # y needs to be cast to float: ITOF
        # then float addition: ADDF
        self.assertIn("PUSHOFF 0", code)
        self.assertIn("PUSHOFF 1", code)
        
        # Find index of PUSHOFF 1 and make sure ITOF appears after it and before ADDF
        idx_push_y = code.find("PUSHOFF 1")
        idx_itof = code.find("ITOF", idx_push_y)
        idx_addf = code.find("ADDF", idx_itof)
        
        self.assertNotEqual(idx_push_y, -1)
        self.assertNotEqual(idx_itof, -1)
        self.assertNotEqual(idx_addf, -1)
        self.assertTrue(idx_push_y < idx_itof < idx_addf)

    def test_implicit_casting_ftoi_on_assignment(self):
        # Storing a float into an int variable
        source = (
            "hobbit x is 5.5 ."
        )
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        gen = CodeGenerator(ast)
        code = gen.generate()
        
        # PUSHIMMF 5.5 -> FTOI -> STOREOFF 0
        self.assertIn("PUSHIMMF 5.5", code)
        self.assertIn("FTOI", code)
        self.assertIn("STOREOFF 0", code)
        
        idx_push = code.find("PUSHIMMF 5.5")
        idx_ftoi = code.find("FTOI", idx_push)
        idx_store = code.find("STOREOFF 0", idx_ftoi)
        self.assertTrue(idx_push < idx_ftoi < idx_store)

    def test_float_remainder(self):
        # remainder between two floats
        source = (
            "dwarf z is 5.5 remainder 2.0 ."
        )
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        gen = CodeGenerator(ast)
        code = gen.generate()
        
        # Should push 5.5, convert to int (FTOI), push 2.0, convert to int (FTOI), run MOD, convert back to float (ITOF)
        self.assertIn("PUSHIMMF 5.5", code)
        self.assertIn("PUSHIMMF 2.0", code)
        self.assertIn("FTOI", code)
        self.assertIn("MOD", code)
        self.assertIn("ITOF", code)

    def test_undeclared_variable_error(self):
        # x is used before declaration
        source = "hobbit y is x plus 5 ."
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        gen = CodeGenerator(ast)
        
        with self.assertRaises(SemanticError):
            gen.generate()

    def test_declare_before_use_error_in_self_assign(self):
        # hobbit x is x . (illegal since x is not yet declared during evaluation of right hand side)
        source = "hobbit x is x ."
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        gen = CodeGenerator(ast)
        
        with self.assertRaises(SemanticError):
            gen.generate()

    def test_remainder_divisor_safety(self):
        # dwarf remainder
        source = "dwarf z is 5.5 remainder (0.0 minus 0.5) ."
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        gen = CodeGenerator(ast)
        code = gen.generate()
        
        # Verify safety check labels and instructions are generated
        self.assertIn("rem_make_pos_", code)
        self.assertIn("rem_clamp_one_", code)
        self.assertIn("PUSHIMMF -1.0", code)
        self.assertIn("PUSHIMMF 1.0", code)
        
        # hobbit remainder
        source_int = "hobbit y is 5 remainder (0 minus 2) ."
        tokens_int = tokenize(source_int)
        parser_int = Parser(tokens_int)
        ast_int = parser_int.parse()
        gen_int = CodeGenerator(ast_int)
        code_int = gen_int.generate()
        
        self.assertIn("rem_make_pos_int_", code_int)
        self.assertIn("PUSHIMM -1", code_int)

if __name__ == '__main__':
    unittest.main()
