# File Research: sources/os/plan9/9front/sys/src/cmd/forp/parse.c

## Purpose
Lexes and parses the `forp` input language into declarations, assumptions, proof goals, and expressions.

## Key Elements
Recognizes keywords `bit`, `signed`, `assume`, and `obviously`; parses numeric literals, symbols, comments, multi-character operators, precedence-based expressions, indexing/slices, ternary expressions, declarations with optional bit width, assumptions, proof goals, and expression statements. Installs token and expression formatters.

## Dependencies
Uses Bio input, Plan 9 `mpint`, symbol interning, AST construction, conversion, and assertion APIs.

## Behavior/Risks
Block-comment lexing scans until `*/` without explicit EOF diagnostics in the inner loop. Operators and keyword jump tables rely on sorted static tables. Undefined symbols and nonconstant indexes are rejected during parse/convert.
