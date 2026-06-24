import unittest
from src.lexer import tokenize
from src.parser import Parser, ParserSyntaxError, BinOpNode, AssignmentNode, QuestNode, SeekNode

class TestParser(unittest.TestCase):
    def test_valid_assignments(self):
        source = (
            "hobbit x is 5 .\n"
            "x is 10 .\n"
            "dwarf y is 3.14 ."
        )
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast.statements), 3)
        self.assertTrue(isinstance(ast.statements[0], AssignmentNode))
        self.assertEqual(ast.statements[0].var_type, 'hobbit')
        self.assertEqual(ast.statements[0].identifier, 'x')
        
        self.assertTrue(isinstance(ast.statements[1], AssignmentNode))
        self.assertEqual(ast.statements[1].var_type, None)
        self.assertEqual(ast.statements[1].identifier, 'x')
        
        self.assertTrue(isinstance(ast.statements[2], AssignmentNode))
        self.assertEqual(ast.statements[2].var_type, 'dwarf')
        self.assertEqual(ast.statements[2].identifier, 'y')

    def test_left_leaning_precedence(self):
        source = "x is a plus b multiply c minus d ."
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        
        # AST should represent: (a plus (b multiply c)) minus d
        # Top-level expression of assignment is minus
        expr = ast.statements[0].expression
        self.assertTrue(isinstance(expr, BinOpNode))
        self.assertEqual(expr.op, 'minus')
        self.assertEqual(expr.right.identifier, 'd')
        
        # Left child of minus is plus
        left_of_minus = expr.left
        self.assertTrue(isinstance(left_of_minus, BinOpNode))
        self.assertEqual(left_of_minus.op, 'plus')
        self.assertEqual(left_of_minus.left.identifier, 'a')
        
        # Right child of plus is multiply
        right_of_plus = left_of_minus.right
        self.assertTrue(isinstance(right_of_plus, BinOpNode))
        self.assertEqual(right_of_plus.op, 'multiply')
        self.assertEqual(right_of_plus.left.identifier, 'b')
        self.assertEqual(right_of_plus.right.identifier, 'c')

    def test_valid_quest_and_seek(self):
        source = (
            "quest (x greater y) {\n"
            "  x is y .\n"
            "} fulfilled unless {\n"
            "  y is x .\n"
            "}\n"
            "seek (x less 100) {\n"
            "  x is x plus 1 .\n"
            "}"
        )
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast.statements), 2)
        
        # QuestNode check
        self.assertTrue(isinstance(ast.statements[0], QuestNode))
        self.assertEqual(ast.statements[0].condition.relop, 'greater')
        self.assertEqual(len(ast.statements[0].then_block), 1)
        self.assertEqual(len(ast.statements[0].else_block), 1)
        
        # SeekNode check
        self.assertTrue(isinstance(ast.statements[1], SeekNode))
        self.assertEqual(ast.statements[1].condition.relop, 'less')
        self.assertEqual(len(ast.statements[1].body), 1)

    def test_invalid_syntax_missing_dot(self):
        source = "hobbit x is 5"
        tokens = tokenize(source)
        parser = Parser(tokens)
        with self.assertRaises(ParserSyntaxError):
            parser.parse()

    def test_invalid_syntax_quest_missing_unless(self):
        source = (
            "quest (x equal y) {\n"
            "  x is y .\n"
            "} fulfilled"
        )
        tokens = tokenize(source)
        parser = Parser(tokens)
        with self.assertRaises(ParserSyntaxError):
            parser.parse()

if __name__ == '__main__':
    unittest.main()
