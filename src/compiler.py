import sys
import os
from src.preprocessor import preprocess
from src.lexer import tokenize, LexicalError
from src.parser import Parser, ParserSyntaxError
from src.generator import CodeGenerator, SemanticError

def compile_clotr(source_code: str) -> str:
    """
    Compiles CLOTR source code into SaM assembly code.
    """
    # TO-DO
    # 1. Preprocessor
    clean_code = preprocess(source_code)
    
    # 2. Lexer
    tokens = tokenize(clean_code)
    
    # 3. Parser
    parser = Parser(tokens)
    ast = parser.parse()
    
    # 4. Generator 
    generator = CodeGenerator(ast)
    return generator.generate()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compiler.py <input.clotr> [output.sam]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # default
        base, _ = os.path.splitext(input_file)
        output_file = base + ".sam"
        
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
            
        sam_code = compile_clotr(source)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sam_code)
            
        print(f"Successfully compiled {input_file} to {output_file}")
        
    except (LexicalError, ParserSyntaxError, SemanticError) as e:
        print(f"Compilation Failed:\n{e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during compilation: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()
