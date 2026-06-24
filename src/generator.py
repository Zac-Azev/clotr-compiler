import sys
from src.parser import (
    ASTNode, ProgramNode, AssignmentNode, QuestNode, SeekNode, 
    BinOpNode, ConditionNode, VarNode, NumNode, CharNode
)

class SemanticError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"Semantic Error: {message} at line {line}")
        self.line = line

class CodeGenerator:
    def __init__(self, ast: ProgramNode):
        self.ast = ast
        self.symbol_table = {}
        self.next_offset = 0
        self.label_counter = 0
        self.instructions = []

    def new_label(self, prefix: str) -> str:
        label = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label
    #helping with implicit type redefinition
    def get_expr_type(self, node: ASTNode) -> str:
        if isinstance(node, NumNode):
            return 'dwarf' if '.' in node.value else 'hobbit'
        elif isinstance(node, CharNode):
            return 'elf'
        elif isinstance(node, VarNode):
            if node.identifier not in self.symbol_table:
                raise SemanticError(f"Undeclared variable '{node.identifier}' used in expression", node.line)
            return self.symbol_table[node.identifier]['type']
        elif isinstance(node, BinOpNode):
            t_left = self.get_expr_type(node.left)
            t_right = self.get_expr_type(node.right)
            if t_left == 'dwarf' or t_right == 'dwarf':
                return 'dwarf'
            return 'hobbit'
        elif isinstance(node, ConditionNode):
            # Evaluate operand types to ensure they are defined
            self.get_expr_type(node.left)
            self.get_expr_type(node.right)
            return 'hobbit'  # Conditions result in boolean (int)
        else:
            raise SemanticError("Unknown expression node type", 0)

    def analyze_and_declare(self) -> None:
        
        # Performs a sequential pass over the AST statements to:
        # 1. Enforce declare-before-use (scanning expression of assignment before declaring variable).
        # 2. Populate symbol table with offsets and types.
        # 3. Count total variables.
        
        self.symbol_table = {}
        self.next_offset = 0
        self._analyze_statements(self.ast.statements)

    def _analyze_statements(self, statements: list[ASTNode]) -> None:
        for stmt in statements:
            if isinstance(stmt, AssignmentNode):
                # 1. Analyze the right-hand expression first
                self.get_expr_type(stmt.expression)
                
                # 2. Declare or update variable type
                if stmt.var_type is not None:
                    if stmt.identifier not in self.symbol_table:
                        self.symbol_table[stmt.identifier] = {
                            'offset': self.next_offset,
                            'type': stmt.var_type
                        }
                        self.next_offset += 1
                    else:
                        # Re-declaration: update type, keep offset
                        self.symbol_table[stmt.identifier]['type'] = stmt.var_type
                else:
                    if stmt.identifier not in self.symbol_table:
                        raise SemanticError(f"Undeclared variable '{stmt.identifier}'", stmt.line)
            
            elif isinstance(stmt, QuestNode):
                self.get_expr_type(stmt.condition)
                self._analyze_statements(stmt.then_block)
                self._analyze_statements(stmt.else_block)
                
            elif isinstance(stmt, SeekNode):
                self.get_expr_type(stmt.condition)
                self._analyze_statements(stmt.body)
                
            else:
                # Standalone expression
                self.get_expr_type(stmt)

    def emit(self, instruction: str) -> None:
        self.instructions.append(instruction)

    def generate(self) -> str:
        # 1. Validate semantics and populate symbol table
        self.analyze_and_declare()
        
        # 2. Emit entry boilerplate (allocation of local variables)
        num_vars = self.next_offset
        self.emit(f"ADDSP {num_vars}")
        
        # 3. Generate code for statements
        self.generate_statements(self.ast.statements)
        
        # 4. Emit exit boilerplate
        self.emit(f"ADDSP -{num_vars}")
        self.emit("PUSHIMM 0")
        self.emit("STOP")
        
        return "\n".join(self.instructions) + "\n"

    def generate_statements(self, statements: list[ASTNode]) -> None:
        for stmt in statements:
            self.generate_statement(stmt)

    def generate_statement(self, stmt: ASTNode) -> None:
        if isinstance(stmt, AssignmentNode):
            # Evaluate expression (pushes to stack)
            self.generate_expression(stmt.expression)
            
            # Determine type of expression and target variable
            t_expr = self.get_expr_type(stmt.expression)
            t_var = self.symbol_table[stmt.identifier]['type']
            
            # Perform casting if necessary
            if t_var == 'dwarf' and t_expr != 'dwarf':
                self.emit("ITOF")
            elif t_var != 'dwarf' and t_expr == 'dwarf':
                self.emit("FTOI")
                
            # Store into stack
            offset = self.symbol_table[stmt.identifier]['offset']
            self.emit(f"STOREOFF {offset}")
            
        elif isinstance(stmt, QuestNode):
            label_else = self.new_label("else")
            label_end = self.new_label("end_quest")
            
            # 1. Evaluate condition
            self.generate_condition(stmt.condition)
            self.emit("ISNIL")
            self.emit(f"JUMPC {label_else}")
            
            # 2. Then block
            self.generate_statements(stmt.then_block)
            self.emit(f"JUMP {label_end}")
            
            # 3. Else block
            self.emit(f"{label_else}:")
            self.generate_statements(stmt.else_block)
            
            # 4. End label
            self.emit(f"{label_end}:")
            
        elif isinstance(stmt, SeekNode):
            label_start = self.new_label("seek_start")
            label_end = self.new_label("seek_end")
            
            # 1. Start label
            self.emit(f"{label_start}:")
            
            # 2. Evaluate condition
            self.generate_condition(stmt.condition)
            self.emit("ISNIL")
            self.emit(f"JUMPC {label_end}")
            
            # 3. Body
            self.generate_statements(stmt.body)
            self.emit(f"JUMP {label_start}")
            
            # 4. End label
            self.emit(f"{label_end}:")
            
        else:
            # Standalone expression
            self.generate_expression(stmt)
            # Standalone expression result needs to be discarded to prevent stack growth
            self.emit("ADDSP -1")

    def generate_expression(self, expr: ASTNode) -> None:
        if isinstance(expr, NumNode):
            if '.' in expr.value:
                self.emit(f"PUSHIMMF {expr.value}")
            else:
                self.emit(f"PUSHIMM {expr.value}")
                
        elif isinstance(expr, CharNode):
            # Strips quotes from char representation, e.g., "'a'" -> "a"
            char_val = expr.value[1:-1]
            self.emit(f"PUSHIMMCH {char_val}")
            
        elif isinstance(expr, VarNode):
            offset = self.symbol_table[expr.identifier]['offset']
            self.emit(f"PUSHOFF {offset}")
            
        elif isinstance(expr, BinOpNode):
            # Determine types and resolution
            t_left = self.get_expr_type(expr.left)
            t_right = self.get_expr_type(expr.right)
            is_float = (t_left == 'dwarf' or t_right == 'dwarf')
            
            if expr.op == 'remainder' and is_float:
                # Modulo operation on floats: cast operands to ints, do MOD, and cast result back if float resolution.
                self.generate_expression(expr.left)
                if t_left == 'dwarf':
                    self.emit("FTOI")
                    
                self.generate_expression(expr.right)
                if t_right == 'dwarf':
                    # Apply float divisor safety rules
                    lbl_make_pos = self.new_label("rem_make_pos")
                    lbl_check_clamp = self.new_label("rem_check_clamp")
                    lbl_gr_zero = self.new_label("rem_gr_zero")
                    lbl_end_check = self.new_label("rem_end_check")
                    lbl_clamp_one = self.new_label("rem_clamp_one")
                    
                    # Absolute value
                    self.emit("DUP")
                    self.emit("PUSHIMMF 0.0")
                    self.emit("CMPF")
                    self.emit("ISNEG")
                    self.emit(f"JUMPC {lbl_make_pos}")
                    self.emit(f"JUMP {lbl_check_clamp}")
                    self.emit(f"{lbl_make_pos}:")
                    self.emit("PUSHIMMF -1.0")
                    self.emit("TIMESF")
                    self.emit(f"{lbl_check_clamp}:")
                    
                    # Clamp 0 < x < 1 to 1.0
                    self.emit("DUP")
                    self.emit("PUSHIMMF 1.0")
                    self.emit("CMPF")
                    self.emit("ISNEG")
                    self.emit(f"JUMPC {lbl_gr_zero}")
                    self.emit(f"JUMP {lbl_end_check}")
                    self.emit(f"{lbl_gr_zero}:")
                    self.emit("DUP")
                    self.emit("PUSHIMMF 0.0")
                    self.emit("CMPF")
                    self.emit("ISPOS")
                    self.emit(f"JUMPC {lbl_clamp_one}")
                    self.emit(f"JUMP {lbl_end_check}")
                    self.emit(f"{lbl_clamp_one}:")
                    self.emit("ADDSP -1")
                    self.emit("PUSHIMMF 1.0")
                    self.emit(f"{lbl_end_check}:")
                    
                    self.emit("FTOI")
                else:
                    # Divisor is integer (t_right == 'hobbit')
                    lbl_make_pos_int = self.new_label("rem_make_pos_int")
                    lbl_end_int = self.new_label("rem_end_int")
                    
                    self.emit("DUP")
                    self.emit("ISNEG")
                    self.emit(f"JUMPC {lbl_make_pos_int}")
                    self.emit(f"JUMP {lbl_end_int}")
                    self.emit(f"{lbl_make_pos_int}:")
                    self.emit("PUSHIMM -1")
                    self.emit("TIMES")
                    self.emit(f"{lbl_end_int}:")
                    
                self.emit("MOD")
                self.emit("ITOF")
            else:
                # 1. Left operand
                self.generate_expression(expr.left)
                if is_float and t_left != 'dwarf':
                    self.emit("ITOF")
                    
                # 2. Right operand
                self.generate_expression(expr.right)
                if is_float and t_right != 'dwarf':
                    self.emit("ITOF")
                    
                # 3. Instruction emission
                if is_float:
                    if expr.op == 'plus':
                        self.emit("ADDF")
                    elif expr.op == 'minus':
                        self.emit("SUBF")
                    elif expr.op == 'multiply':
                        self.emit("TIMESF")
                    elif expr.op == 'divide':
                        self.emit("DIVF")
                else:
                    if expr.op == 'plus':
                        self.emit("ADD")
                    elif expr.op == 'minus':
                        self.emit("SUB")
                    elif expr.op == 'multiply':
                        self.emit("TIMES")
                    elif expr.op == 'divide':
                        self.emit("DIV")
                    elif expr.op == 'remainder':
                        lbl_make_pos_int = self.new_label("rem_make_pos_int")
                        lbl_end_int = self.new_label("rem_end_int")
                        
                        self.emit("DUP")
                        self.emit("ISNEG")
                        self.emit(f"JUMPC {lbl_make_pos_int}")
                        self.emit(f"JUMP {lbl_end_int}")
                        self.emit(f"{lbl_make_pos_int}:")
                        self.emit("PUSHIMM -1")
                        self.emit("TIMES")
                        self.emit(f"{lbl_end_int}:")
                        self.emit("MOD")

    def generate_condition(self, cond: ConditionNode) -> None:
        t_left = self.get_expr_type(cond.left)
        t_right = self.get_expr_type(cond.right)
        is_float = (t_left == 'dwarf' or t_right == 'dwarf')
        
        # 1. Generate Left
        self.generate_expression(cond.left)
        if is_float and t_left != 'dwarf':
            self.emit("ITOF")
            
        # 2. Generate Right
        self.generate_expression(cond.right)
        if is_float and t_right != 'dwarf':
            self.emit("ITOF")
            
        # 3. Emit comparison
        if is_float:
            self.emit("CMPF")
            if cond.relop == 'equal':
                self.emit("NOT")
            elif cond.relop == 'not_equal':
                self.emit("NOT")
                self.emit("NOT")
            elif cond.relop == 'greater':
                self.emit("ISPOS")
            elif cond.relop == 'less':
                self.emit("ISNEG")
            elif cond.relop == 'greater_or_equal':
                self.emit("ISNEG")
                self.emit("NOT")
            elif cond.relop == 'less_or_equal':
                self.emit("ISPOS")
                self.emit("NOT")
        else:
            if cond.relop == 'equal':
                self.emit("EQUAL")
            elif cond.relop == 'not_equal':
                self.emit("EQUAL")
                self.emit("NOT")
            elif cond.relop == 'greater':
                self.emit("GREATER")
            elif cond.relop == 'less':
                self.emit("LESS")
            elif cond.relop == 'greater_or_equal':
                self.emit("LESS")
                self.emit("NOT")
            elif cond.relop == 'less_or_equal':
                self.emit("GREATER")
                self.emit("NOT")

if __name__ == '__main__':
    from src.lexer import tokenize
    from src.parser import Parser
    if len(sys.argv) < 2:
        print("Usage: python3 generator.py <clean_file.clean>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        src = f.read()
    try:
        tks = tokenize(src)
        parser = Parser(tks)
        ast = parser.parse()
        gen = CodeGenerator(ast)
        sam_code = gen.generate()
        print(sam_code)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
