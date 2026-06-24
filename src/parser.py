import sys
from src.lexer import (
    Token, 
    TOKEN_TYPE_TYPE, 
    TOKEN_TYPE_IDENTIFIER, 
    TOKEN_TYPE_NUMBER, 
    TOKEN_TYPE_CHARACTER, 
    TOKEN_TYPE_KEYWORD, 
    TOKEN_TYPE_RELOP, 
    TOKEN_TYPE_OPERATOR, 
    TOKEN_TYPE_LPAREN, 
    TOKEN_TYPE_RPAREN, 
    TOKEN_TYPE_LBRACE, 
    TOKEN_TYPE_RBRACE,
    TOKEN_TYPE_DOT
)

class ParserSyntaxError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Syntax Error: {message} at line {line}, column {column}")
        self.line = line
        self.column = column

# AST Nodes representation
class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements: list[ASTNode]):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode({self.statements})"

class AssignmentNode(ASTNode):
    def __init__(self, var_type: str | None, identifier: str, expression: ASTNode, line: int):
        self.var_type = var_type  # e.g., 'hobbit', 'dwarf', 'elf' or None
        self.identifier = identifier
        self.expression = expression
        self.line = line

    def __repr__(self):
        return f"AssignmentNode({self.var_type}, '{self.identifier}', {self.expression})"

class QuestNode(ASTNode):
    def __init__(self, condition: ASTNode, then_block: list[ASTNode], else_block: list[ASTNode], line: int):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        self.line = line

    def __repr__(self):
        return f"QuestNode({self.condition}, then={self.then_block}, else={self.else_block})"

class SeekNode(ASTNode):
    def __init__(self, condition: ASTNode, body: list[ASTNode], line: int):
        self.condition = condition
        self.body = body
        self.line = line

    def __repr__(self):
        return f"SeekNode({self.condition}, body={self.body})"

class BinOpNode(ASTNode):
    def __init__(self, op: str, left: ASTNode, right: ASTNode, line: int):
        self.op = op  # 'plus', 'minus', 'multiply', 'divide', 'remainder'
        self.left = left
        self.right = right
        self.line = line

    def __repr__(self):
        return f"BinOpNode('{self.op}', {self.left}, {self.right})"

class ConditionNode(ASTNode):
    def __init__(self, relop: str, left: ASTNode, right: ASTNode, line: int):
        self.relop = relop  # 'equal', 'not_equal', 'greater', 'less', 'greater_or_equal', 'less_or_equal'
        self.left = left
        self.right = right
        self.line = line

    def __repr__(self):
        return f"ConditionNode('{self.relop}', {self.left}, {self.right})"

class VarNode(ASTNode):
    def __init__(self, identifier: str, line: int):
        self.identifier = identifier
        self.line = line

    def __repr__(self):
        return f"VarNode('{self.identifier}')"

class NumNode(ASTNode):
    def __init__(self, value: str, line: int):
        self.value = value
        self.line = line

    def __repr__(self):
        return f"NumNode({self.value})"

class CharNode(ASTNode):
    def __init__(self, value: str, line: int):
        self.value = value  # e.g., "'a'"
        self.line = line

    def __repr__(self):
        return f"CharNode({self.value})"

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset: int = 0) -> Token | None:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def consume(self) -> Token:
        t = self.peek()
        if t is None:
            # Return a dummy EOF token with coordinates from the last known token or (1, 1)
            last_line = self.tokens[-1].line if self.tokens else 1
            last_col = self.tokens[-1].column if self.tokens else 1
            return Token('EOF', 'EOF', last_line, last_col)
        self.pos += 1
        return t

    def check_type(self, token_type: str) -> bool:
        t = self.peek()
        return t is not None and t.type == token_type

    def check_value(self, value: str) -> bool:
        t = self.peek()
        return t is not None and t.value == value

    def expect_type(self, token_type: str) -> Token:
        t = self.peek()
        if t is None or t.type != token_type:
            got = t.type if t else "EOF"
            line = t.line if t else (self.tokens[-1].line if self.tokens else 1)
            col = t.column if t else (self.tokens[-1].column if self.tokens else 1)
            raise ParserSyntaxError(f"Expected token type '{token_type}', but got '{got}'", line, col)
        return self.consume()

    def expect_value(self, value: str) -> Token:
        t = self.peek()
        if t is None or t.value != value:
            got = t.value if t else "EOF"
            line = t.line if t else (self.tokens[-1].line if self.tokens else 1)
            col = t.column if t else (self.tokens[-1].column if self.tokens else 1)
            raise ParserSyntaxError(f"Expected keyword/symbol '{value}', but got '{got}'", line, col)
        return self.consume()

    def parse(self) -> ProgramNode:
        return self.parse_program()

    def parse_program(self) -> ProgramNode:
        statements = self.parse_statement_list()
        # Verify that we consumed all tokens
        if self.peek() is not None:
            t = self.peek()
            raise ParserSyntaxError(f"Unexpected token '{t.value}' at end of program", t.line, t.column)
        return ProgramNode(statements)

    def parse_statement_list(self) -> list[ASTNode]:
        statements = []
        # A statement list ends when we run out of tokens, or hit a closing brace '}'
        # or keywords that signal the end of a block (like 'fulfilled', 'unless')
        while self.peek() is not None:
            t = self.peek()
            if t.type == TOKEN_TYPE_RBRACE or t.value in {'fulfilled', 'unless'}:
                break
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self) -> ASTNode:
        t = self.peek()
        if t is None:
            raise ParserSyntaxError("Unexpected EOF while parsing statement", 1, 1)

        # 1. Assignment or Expression
        if t.type == TOKEN_TYPE_TYPE:
            return self.parse_assignment()
        elif t.type == TOKEN_TYPE_IDENTIFIER:
            return self.parse_identifier_statement()
        
        # 2. Quest
        elif t.value == 'quest':
            return self.parse_quest()
            
        # 3. Seek
        elif t.value == 'seek':
            return self.parse_seek()
            
        # 4. Expression
        else:
            return self.parse_expression()

    def parse_identifier_statement(self) -> ASTNode:
        ident_tok = self.expect_type(TOKEN_TYPE_IDENTIFIER)
        next_t = self.peek()
        if next_t is not None and next_t.value == 'is':
            self.consume()  # Consume 'is'
            expr = self.parse_expression()
            self.expect_type(TOKEN_TYPE_DOT)
            return AssignmentNode(None, ident_tok.value, expr, ident_tok.line)
        else:
            # Standalone expression starting with this identifier
            initial_node = VarNode(ident_tok.value, ident_tok.line)
            return self.parse_expression(initial_node)

    def parse_assignment(self) -> AssignmentNode:
        var_type_tok = self.expect_type(TOKEN_TYPE_TYPE)
        ident_tok = self.expect_type(TOKEN_TYPE_IDENTIFIER)
        self.expect_value('is')
        expr = self.parse_expression()
        self.expect_type(TOKEN_TYPE_DOT)
        
        return AssignmentNode(var_type_tok.value, ident_tok.value, expr, ident_tok.line)

    def parse_quest(self) -> QuestNode:
        quest_tok = self.expect_value('quest')
        self.expect_value('(')
        cond = self.parse_condition()
        self.expect_value(')')
        
        self.expect_value('{')
        then_block = self.parse_statement_list()
        self.expect_value('}')
        
        self.expect_value('fulfilled')
        self.expect_value('unless')
        
        self.expect_value('{')
        else_block = self.parse_statement_list()
        self.expect_value('}')
        
        return QuestNode(cond, then_block, else_block, quest_tok.line)

    def parse_seek(self) -> SeekNode:
        seek_tok = self.expect_value('seek')
        self.expect_value('(')
        cond = self.parse_condition()
        self.expect_value(')')
        
        self.expect_value('{')
        body = self.parse_statement_list()
        self.expect_value('}')
        
        return SeekNode(cond, body, seek_tok.line)

    def parse_condition(self) -> ConditionNode:
        left = self.parse_expression()
        
        # Relational operator
        relop_tok = self.expect_type(TOKEN_TYPE_RELOP)
        
        right = self.parse_expression()
        return ConditionNode(relop_tok.value, left, right, relop_tok.line)

    def parse_expression(self, initial_node: ASTNode = None) -> ASTNode:
        left = self.parse_term(initial_node)
        # Parse left-leaning expressionprime
        while self.peek() is not None:
            t = self.peek()
            if t.value in {'plus', 'minus'}:
                op_tok = self.consume()
                right = self.parse_term()
                left = BinOpNode(op_tok.value, left, right, op_tok.line)
            else:
                break
        return left

    def parse_term(self, initial_node: ASTNode = None) -> ASTNode:
        if initial_node is not None:
            left = initial_node
        else:
            left = self.parse_factor()
        # Parse left-leaning termprime
        while self.peek() is not None:
            t = self.peek()
            if t.value in {'multiply', 'divide', 'remainder'}:
                op_tok = self.consume()
                right = self.parse_factor()
                left = BinOpNode(op_tok.value, left, right, op_tok.line)
            else:
                break
        return left

    def parse_factor(self) -> ASTNode:
        t = self.peek()
        if t is None:
            raise ParserSyntaxError("Unexpected EOF while parsing factor", 1, 1)
            
        if t.type == TOKEN_TYPE_IDENTIFIER:
            tok = self.consume()
            return VarNode(tok.value, tok.line)
        elif t.type == TOKEN_TYPE_NUMBER:
            tok = self.consume()
            return NumNode(tok.value, tok.line)
        elif t.type == TOKEN_TYPE_CHARACTER:
            tok = self.consume()
            return CharNode(tok.value, tok.line)
        elif t.value == '(':
            self.consume()  # '('
            expr = self.parse_expression()
            self.expect_value(')')
            return expr
        else:
            raise ParserSyntaxError(f"Unexpected token '{t.value}' in expression factor", t.line, t.column)

if __name__ == '__main__':
    from src.lexer import tokenize
    if len(sys.argv) < 2:
        print("Usage: python3 parser.py <clean_file.clean>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        src = f.read()
    try:
        tks = tokenize(src)
        parser = Parser(tks)
        ast = parser.parse()
        print(ast)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
