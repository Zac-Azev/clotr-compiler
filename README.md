# CLOTR Compiler (Compiler in Lord of the Rings)

CLOTR is a top-down, LL(1) procedural compiler targeting the Stack Machine (SaM) assembly architecture. It converts high-level narrative code inspired by D&D and Lord of the Rings style into functional SaM assembly.

## Reorganized Project Structure

The project has been organized into clean, modular directories:

```
compiladores_Clotr/
├── src/                    # Compiler package source code
│   ├── __init__.py
│   ├── preprocessor.py     # Strips #editor-note sections
│   ├── lexer.py            # Generates regex-based tokens
│   ├── parser.py           # LL(1) recursive descent parser
│   ├── generator.py        # Walks AST and emits SaM assembly
│   └── compiler.py         # Main CLI entry point
│
├── tests/                  # Package unit and integration tests
│   ├── __init__.py
│   ├── test_preprocessor.py
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_generator.py
│   └── test_compiler.py
│
├── docs/                   # Documentation and course requirements
│   ├── SaM-wiki.md
│   ├── clotrIdeation.md
│   ├── grammar.md
│   ├── assembly-sam.pdf / txt
│   └── requisitos-da-linguagem-programacao.pdf / txt
│
├── examples/               # Sample CLOTR scripts and target output
│   ├── snippet.clotr
│   ├── snippet.sam
│   └── no-snippet.clotr
│
├── material-sam/           # SaM virtual machine Jar files
│   └── SaM-2.6.3.jar
│
├── CHECKLIST.md            # Requisite progress tracking
└── GEMINI.md               # Compiler architect directives
```

---

## Command Reference & Getting Started

Here are the scripts and commands available in this project for compiling, running, and testing CLOTR programs.

### 1. Compile CLOTR Code (`compile.sh`)
Compiles a `.clotr` source file into a `.sam` stack machine assembly file.
- **Syntax:**
  ```bash
  ./compile.sh <input_file.clotr>
  ```
- **Example:**
  ```bash
  ./compile.sh examples/snippet.clotr
  ```
  This creates `examples/snippet.sam`.

### 2. Compile and Open in SaM GUI (`compile-sam.sh`)
Compiles a `.clotr` file and opens the compiled `.sam` assembly file in the SaM graphical user interface (GUI) simulator.
- **Syntax:**
  ```bash
  [UI_SCALE=scaling_factor] ./compile-sam.sh <input_file.clotr>
  ```
- **Example:**
  ```bash
  ./compile-sam.sh examples/snippet.clotr
  ```
  For high-DPI screens, you can scale the UI by prepending `UI_SCALE`:
  ```bash
  UI_SCALE=2.5 ./compile-sam.sh examples/snippet.clotr
  ```
  *(Note: Requires Java/JVM installed on your local machine).*

### 3. Run the Test Suite (`run-tests`)
Executes all unit and integration tests (validating the preprocessor, lexer, parser, generator, and compiler) in the `tests/` directory.
- **Syntax:**
  ```bash
  ./run-tests [unittest_options]
  ```
- **Example:**
  ```bash
  ./run-tests
  ```
  For verbose test output:
  ```bash
  ./run-tests -v
  ```

---

### Manual Python Commands

If you prefer to run the tools without the wrapper scripts, you can execute the Python modules directly:

#### Manual Compile
- **Syntax:**
  ```bash
  python3 -m src.compiler <input_file.clotr> [output_file.sam]
  ```
- **Example:**
  ```bash
  python3 -m src.compiler examples/snippet.clotr custom_output.sam
  ```

#### Manual Run Tests
- **Syntax:**
  ```bash
  python3 -m unittest discover -s tests -p "test_*.py" [unittest_options]
  ```
- **Example:**
  ```bash
  python3 -m unittest discover -s tests -p "test_*.py" -v
  ```

---

## CLOTR Syntax Overview

### Types
- `hobbit` (integers)
- `dwarf` (floats)
- `elf` (characters)

### Declarations and Reassignments
Variable declarations require specifying the type:
```clotr
hobbit Frodo is 5 .
dwarf Sam is 10.5 .
elf Gandalf is 'G' .
```

Reassigning an existing variable does not require repeating the type (unless doing implicit casting):
```clotr
Frodo is 10 .
```

### Operator Precedence (Left-Leaning)
Operators are keywords instead of symbols:
* **Additive:** `plus`, `minus`
* **Multiplicative:** `multiply`, `divide`, `remainder`

Example:
```clotr
hobbit x is a plus b multiply c minus d .
```
This is evaluated left-to-right as `((a plus (b multiply c)) minus d)`.

### Decisions (`quest`)
Maps to an `if/then/else` construct. The condition is evaluated, block 1 (then) is run if true, and block 2 (else/unless) is run if false:
```clotr
quest (Sam greater_or_equal 3.0) {
  Sam is Sam minus 1.0 .
} fulfilled unless {
  Sam is Sam plus 0.5 .
}
```

### Loops (`seek`)
Maps to a `while` loop construct:
```clotr
seek (Frodo less 5) {
  Frodo is Frodo plus 1 .
}
```
