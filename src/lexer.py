import re
import sys

# Define constants for Token Types
TOKEN_TYPE_TYPE = 'TYPE'
TOKEN_TYPE_IDENTIFIER = 'IDENTIFIER'
TOKEN_TYPE_NUMBER = 'NUMBER'
TOKEN_TYPE_CHARACTER = 'CHARACTER'
TOKEN_TYPE_KEYWORD = 'KEYWORD'
TOKEN_TYPE_RELOP = 'RELOP'
TOKEN_TYPE_OPERATOR = 'OPERATOR'
TOKEN_TYPE_LPAREN = 'LPAREN'
TOKEN_TYPE_RPAREN = 'RPAREN'
TOKEN_TYPE_LBRACE = 'LBRACE'
TOKEN_TYPE_RBRACE = 'RBRACE'
TOKEN_TYPE_DOT = 'DOT'

# Categorization sets
TYPES = {'hobbit', 'dwarf', 'elf'}
KEYWORDS = {'quest', 'fulfilled', 'unless', 'seek', 'is'}
RELOPS = {'equal', 'not_equal', 'greater', 'less', 'greater_or_equal', 'less_or_equal'}
OPERATORS = {'plus', 'minus', 'multiply', 'divide', 'remainder'}

class Token:
    def __init__(self, token_type: str, value: str, line: int, column: int):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (self.type == other.type and 
                self.value == other.value and 
                self.line == other.line and 
                self.column == other.column)

class LexicalError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"{message} at line {line}, column {column}")
        self.line = line
        self.column = column

def tokenize(source: str) -> list[Token]:
    tokens = []
    
    # Compile regexes. Note that we match from the current position.
    number_regex = re.compile(r'\d+(?:\.\d+)?')
    char_regex = re.compile(r"'[a-zA-Z0-9]'")
    ident_regex = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    
    line = 1
    column = 1
    pos = 0
    length = len(source)
    
    while pos < length:
        current_char = source[pos]
        
        # 1. Handle Whitespace
        if current_char == '\n':
            line += 1
            column = 1
            pos += 1
            continue
        elif current_char.isspace():
            column += 1
            pos += 1
            continue
            
        # 2. Simple Symbols
        if current_char == '(':
            tokens.append(Token(TOKEN_TYPE_LPAREN, '(', line, column))
            column += 1
            pos += 1
            continue
        elif current_char == ')':
            tokens.append(Token(TOKEN_TYPE_RPAREN, ')', line, column))
            column += 1
            pos += 1
            continue
        elif current_char == '{':
            tokens.append(Token(TOKEN_TYPE_LBRACE, '{', line, column))
            column += 1
            pos += 1
            continue
        elif current_char == '}':
            tokens.append(Token(TOKEN_TYPE_RBRACE, '}', line, column))
            column += 1
            pos += 1
            continue
        elif current_char == '.':
            tokens.append(Token(TOKEN_TYPE_DOT, '.', line, column))
            column += 1
            pos += 1
            continue
            
        # 3. Match character literals
        char_match = char_regex.match(source, pos)
        if char_match:
            lexeme = char_match.group(0)
            tokens.append(Token(TOKEN_TYPE_CHARACTER, lexeme, line, column))
            column += len(lexeme)
            pos += len(lexeme)
            continue
            
        # 4. Match numbers
        number_match = number_regex.match(source, pos)
        if number_match:
            lexeme = number_match.group(0)
            tokens.append(Token(TOKEN_TYPE_NUMBER, lexeme, line, column))
            column += len(lexeme)
            pos += len(lexeme)
            continue
            
        # 5. Match identifiers and words (keywords, types, relops, operators)
        ident_match = ident_regex.match(source, pos)
        if ident_match:
            lexeme = ident_match.group(0)
            
            # Categorize the matched identifier
            if lexeme in TYPES:
                token_type = TOKEN_TYPE_TYPE
            elif lexeme in KEYWORDS:
                token_type = TOKEN_TYPE_KEYWORD
            elif lexeme in RELOPS:
                token_type = TOKEN_TYPE_RELOP
            elif lexeme in OPERATORS:
                token_type = TOKEN_TYPE_OPERATOR
            else:
                token_type = TOKEN_TYPE_IDENTIFIER
                
            tokens.append(Token(token_type, lexeme, line, column))
            column += len(lexeme)
            pos += len(lexeme)
            continue
            
        # 6. Lexical error: unexpected character
        raise LexicalError(f"Unexpected character '{current_char}'", line, column)
        
    return tokens

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 lexer.py <clean_file.clean>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        src = f.read()
    try:
        tks = tokenize(src)
        for t in tks:
            print(t)
    except LexicalError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
