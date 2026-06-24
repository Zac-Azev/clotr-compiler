import unittest
from src.lexer import tokenize, LexicalError, Token, TOKEN_TYPE_TYPE, TOKEN_TYPE_IDENTIFIER, TOKEN_TYPE_NUMBER, TOKEN_TYPE_CHARACTER, TOKEN_TYPE_KEYWORD, TOKEN_TYPE_RELOP, TOKEN_TYPE_OPERATOR, TOKEN_TYPE_LPAREN, TOKEN_TYPE_RPAREN, TOKEN_TYPE_LBRACE, TOKEN_TYPE_RBRACE, TOKEN_TYPE_DOT

class TestLexer(unittest.TestCase):
    def test_types_and_keywords(self):
        source = "hobbit dwarf elf quest fulfilled unless seek is"
        tokens = tokenize(source)
        
        expected_types = [TOKEN_TYPE_TYPE] * 3 + [TOKEN_TYPE_KEYWORD] * 5
        expected_values = ["hobbit", "dwarf", "elf", "quest", "fulfilled", "unless", "seek", "is"]
        
        self.assertEqual(len(tokens), len(expected_values))
        for token, t_type, val in zip(tokens, expected_types, expected_values):
            self.assertEqual(token.type, t_type)
            self.assertEqual(token.value, val)

    def test_relops_and_operators(self):
        source = "equal not_equal greater less greater_or_equal less_or_equal plus minus multiply divide remainder"
        tokens = tokenize(source)
        
        expected_types = [TOKEN_TYPE_RELOP] * 6 + [TOKEN_TYPE_OPERATOR] * 5
        expected_values = [
            "equal", "not_equal", "greater", "less", "greater_or_equal", "less_or_equal",
            "plus", "minus", "multiply", "divide", "remainder"
        ]
        
        self.assertEqual(len(tokens), len(expected_values))
        for token, t_type, val in zip(tokens, expected_types, expected_values):
            self.assertEqual(token.type, t_type)
            self.assertEqual(token.value, val)

    def test_numbers_and_characters(self):
        source = "42 3.14159 'a' '9' 'Z'"
        tokens = tokenize(source)
        
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0].type, TOKEN_TYPE_NUMBER)
        self.assertEqual(tokens[0].value, "42")
        self.assertEqual(tokens[1].type, TOKEN_TYPE_NUMBER)
        self.assertEqual(tokens[1].value, "3.14159")
        self.assertEqual(tokens[2].type, TOKEN_TYPE_CHARACTER)
        self.assertEqual(tokens[2].value, "'a'")
        self.assertEqual(tokens[3].type, TOKEN_TYPE_CHARACTER)
        self.assertEqual(tokens[3].value, "'9'")
        self.assertEqual(tokens[4].type, TOKEN_TYPE_CHARACTER)
        self.assertEqual(tokens[4].value, "'Z'")

    def test_identifiers(self):
        source = "myVariable _myVar var_123"
        tokens = tokenize(source)
        
        self.assertEqual(len(tokens), 3)
        for token in tokens:
            self.assertEqual(token.type, TOKEN_TYPE_IDENTIFIER)
        self.assertEqual(tokens[0].value, "myVariable")
        self.assertEqual(tokens[1].value, "_myVar")
        self.assertEqual(tokens[2].value, "var_123")

    def test_symbols(self):
        source = "() {} ."
        tokens = tokenize(source)
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0].type, TOKEN_TYPE_LPAREN)
        self.assertEqual(tokens[1].type, TOKEN_TYPE_RPAREN)
        self.assertEqual(tokens[2].type, TOKEN_TYPE_LBRACE)
        self.assertEqual(tokens[3].type, TOKEN_TYPE_RBRACE)
        self.assertEqual(tokens[4].type, TOKEN_TYPE_DOT)

    def test_lexical_error(self):
        # Invalid character '@'
        source = "hobbit myVar is 5 @ ."
        with self.assertRaises(LexicalError) as ctx:
            tokenize(source)
        self.assertEqual(ctx.exception.line, 1)
        self.assertEqual(ctx.exception.column, 19)

    def test_lines_and_columns(self):
        source = "hobbit x is 5\ndwarf y is 10.0"
        tokens = tokenize(source)
        
        # hobbit
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)
        
        # x
        self.assertEqual(tokens[1].line, 1)
        self.assertEqual(tokens[1].column, 8)
        
        # dwarf
        self.assertEqual(tokens[4].line, 2)
        self.assertEqual(tokens[4].column, 1)

if __name__ == '__main__':
    unittest.main()
