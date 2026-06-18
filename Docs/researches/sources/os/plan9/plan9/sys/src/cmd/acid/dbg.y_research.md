# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/dbg.y

Yacc grammar for the Acid debugger language.

Key responsibilities:
- Defines parser semantic value types for nodes, symbols, integers, floats, and strings.
- Defines precedence for statements, assignment, formatting, logical/bitwise/arithmetic operators, increments, indirection, field access, indexing, and calls.
- Parses top-level statements, function definitions, function deletion, and complex type definitions.
- Parses control flow: `if/then/else`, `loop`, `while`, `return`, and `local`.
- Parses expressions including casts, unary indirection, arithmetic, shifts, comparisons, logical operations, format suffixes, assignment, list construction, indexing, increment/decrement, field access, calls, builtins, constants, strings, and `what`.
- Constructs Acid AST nodes with `an` and constants with `con`.
- Executes top-level statements immediately and triggers GC afterward.

Dependencies:
- Uses tokens from `lex.c`, AST/node helpers from `main.c`, and evaluator from `exec.c`.

Notable risks:
- Grammar directly constructs executable ASTs; parser and evaluator operation-code enums must stay synchronized.
