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
3.  **Statement** -> AssignmentWithType | Quest | Seek | IDENTIFIER StatementRest | ExpressionNoIdent
4.  **AssignmentWithType** -> Type IDENTIFIER "is" Expression "."
5.  **StatementRest** -> "is" Expression "." | TermPrime ExpressionPrime
6.  **ExpressionNoIdent** -> FactorNoIdent TermPrime ExpressionPrime
7.  **Type** -> "hobbit" | "dwarf" | "elf"
8.  **FactorNoIdent** -> NUMBER | CHARACTER | "(" Expression ")"
9.  **Quest** -> "quest" "(" Condition ")" "{" StatementList "}" "fulfilled" "unless" "{" StatementList "}"
10. **Seek** -> "seek" "(" Condition ")" "{" StatementList "}"
11. **Condition** -> Expression RelationalOperator Expression
12. **Expression** -> Term ExpressionPrime
13. **ExpressionPrime** -> ("plus" | "minus") Term ExpressionPrime | ε
14. **Term** -> Factor TermPrime
15. **TermPrime** -> ("multiply" | "divide" | "remainder") Factor TermPrime | ε
16. **Factor** -> IDENTIFIER | NUMBER | CHARACTER | "(" Expression ")"
17. **RelationalOperator** -> "equal" | "not_equal" | "greater" | "less" | "greater_or_equal" | "less_or_equal"

## FIRST and FOLLOW Sets

Below are the FIRST and FOLLOW sets for all non-terminals in the CLOTR grammar. Symbol `$` represents the End-of-File (EOF) marker.

| Non-Terminal | FIRST Set | FOLLOW Set |
| :--- | :--- | :--- |
| **Program** | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, ε }` | `{ $ }` |
| **StatementList** | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, ε }` | `{ $, }, fulfilled }` |
| **Statement** | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek }` | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **AssignmentWithType** | `{ hobbit, dwarf, elf }` | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **StatementRest** | `{ is, multiply, divide, remainder, plus, minus, ε }` | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **ExpressionNoIdent** | `{ NUMBER, CHARACTER, ( }` | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Type** | `{ hobbit, dwarf, elf }` | `{ IDENTIFIER }` |
| **FactorNoIdent** | `{ NUMBER, CHARACTER, ( }` | `{ multiply, divide, remainder, plus, minus, ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Quest** | `{ quest }` | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Seek** | `{ seek }` | `{ hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Condition** | `{ IDENTIFIER, NUMBER, CHARACTER, ( }` | `{ ) }` |
| **Expression** | `{ IDENTIFIER, NUMBER, CHARACTER, ( }` | `{ ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **ExpressionPrime**| `{ plus, minus, ε }` | `{ ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Term** | `{ IDENTIFIER, NUMBER, CHARACTER, ( }` | `{ plus, minus, ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **TermPrime** | `{ multiply, divide, remainder, ε }` | `{ plus, minus, ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **Factor** | `{ IDENTIFIER, NUMBER, CHARACTER, ( }` | `{ multiply, divide, remainder, plus, minus, ., equal, not_equal, greater, less, greater_or_equal, less_or_equal, ), hobbit, dwarf, elf, IDENTIFIER, NUMBER, CHARACTER, (, quest, seek, $, }, fulfilled }` |
| **RelationalOperator**| `{ equal, not_equal, greater, less, greater_or_equal, less_or_equal }` | `{ IDENTIFIER, NUMBER, CHARACTER, ( }` |

## Left-Factoring Note

Normally, both **Assignment** (specifically re-assignment: `IDENTIFIER "is" ...`) and **Expression** (starting with `IDENTIFIER`) share `IDENTIFIER` in their FIRST sets, which would cause an LL(1) conflict if written naively.

To resolve this conflict formally:
1. The **Statement** production is left-factored by splitting based on whether a statement begins with a `Type`, an `IDENTIFIER`, or another factor (numbers, characters, parenthesis).
2. For statements starting with an `IDENTIFIER`, the parser consumes it and uses the **StatementRest** rules to decide between assignment (`"is" ...`) or expression (`TermPrime ExpressionPrime`).

The compiler's parser implementation implements this left-factoring logic directly to achieve strict LL(1) parsing.
