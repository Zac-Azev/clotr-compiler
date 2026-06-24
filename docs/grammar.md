# CLOTR Language Grammar

This document defines the formal grammar for the CLOTR language. It oughts to be LL(1) compliant, using a left-leaning structure for expression evaluation.

## Terminals (Tokens)
- `TYPE` : `hobbit` | `dwarf` | `elf`
- `IDENTIFIER` : `[a-zA-Z_][a-zA-Z0-9_]*`
- `NUMBER` : `[0-9]+(\.[0-9]+)?`
- `CHARACTER` : `'[a-zA-Z0-9]'`
- `KEYWORD` : `quest` | `fulfilled` | `unless` | `seek` | `is`
- `RELOP` : `equal` | `not_equal` | `greater` | `less` | `greater_or_equal` | `less_or_equal`
- `PLUS` | `MINUS` | `MULTIPLY` | `DIVIDE` | `REMAINDER`
- `(` | `)` | `{` | `}` | `.`

## Productions

1.  **Program** -> StatementList
2.  **StatementList** -> Statement StatementList | ε
3.  **Statement** -> Assignment | Quest | Seek | Expression
4.  **Assignment** -> (Type | ε) IDENTIFIER "is" Expression "."
5.  **Quest** -> "quest" "(" Condition ")" "{" StatementList "}" "fulfilled" "unless" "{" StatementList "}"
6.  **Seek** -> "seek" "(" Condition ")" "{" StatementList "}"
7.  **Type** -> "hobbit" | "dwarf" | "elf"
8.  **Condition** -> Expression RelationalOperator Expression
9.  **Expression** -> Term ExpressionPrime
10. **ExpressionPrime** -> ("plus" | "minus") Term ExpressionPrime | ε
11. **Term** -> Factor TermPrime
12. **TermPrime** -> ("multiply" | "divide" | "remainder") Factor TermPrime | ε
13. **Factor** -> IDENTIFIER | NUMBER | CHARACTER | "(" Expression ")"
14. **RelationalOperator** -> "equal" | "not_equal" | "greater" | "less" | "greater_or_equal" | "less_or_equal"

## FIRST and FOLLOW Sets

Below are the FIRST and FOLLOW sets for all non-terminals in the CLOTR grammar. Symbol `$` represents the End-of-File (EOF) marker.

| Non-Terminal | FIRST Set | FOLLOW Set |
| :--- | :--- | :--- |
| **Program** | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, ε }` | `{ $ }` |
| **StatementList** | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, ε }` | `{ $, }, fulfilled }` |
| **Statement** | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek }` | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Assignment** | `{ hobbit, dwarf, elf, IDENTIFIER }` | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Quest** | `{ quest }` | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Seek** | `{ seek }` | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Type** | `{ hobbit, dwarf, elf }` | `{ IDENTIFIER }` |
| **Condition** | `{ IDENTIFIER, NUMBER, CHARACTER, ( }` | `{ ) }` |
| **Expression** | `{ IDENTIFIER, NUMBER, CHARACTER, ( }` | `{ ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **ExpressionPrime**| `{ plus, minus, ε }` | `{ ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Term** | `{ IDENTIFIER, NUMBER, CHARACTER, ( }` | `{ plus, minus, ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **TermPrime** | `{ multiply, divide, remainder, ε }` | `{ plus, minus, ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Factor** | `{ IDENTIFIER, NUMBER, CHARACTER, ( }` | `{ multiply, divide, remainder, plus, minus, ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **RelationalOperator**| `{ equal, not_equal, greater, less, greater_or_equal, less_or_equal }` | `{ IDENTIFIER, NUMBER, CHARACTER, ( }` |

## Left-Factoring Note

Normally, both **Assignment** (specifically re-assignment: `IDENTIFIER "is" ...`) and **Expression** (starting with `IDENTIFIER`) share `IDENTIFIER` in their FIRST sets, which would cause an LL(1) conflict if written naively.

The parser resolves this conflict using **Left-Factoring**:
1. It consumes the common `IDENTIFIER` first.
2. It then looks at the *new* lookahead token (exactly 1 token of lookahead).
3. If the next token is `"is"`, it parses the rest of the assignment.
4. Otherwise, it passes the consumed identifier to the expression parser as an initial node.

This maintains a strict **LL(1)** parsing decision at every step.
