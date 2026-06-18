# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/prep/calc.y

This yacc grammar parses arithmetic expressions used by the disk partition editors.

Language:
- Numeric literals with optional units: `k`, `m`, `g`, `t`; units convert to sectors with `k` multiplying by 2 and larger units chaining by 1024.
- Special symbols `.` for current dot and `$` for current limit/end.
- Operators: `+`, `-`, `*`, `/`, unary `-`, parentheses, and postfix `%`.
- Postfix `%` evaluates as a percentage of the current size.

Key functions:
- `mkNUM` and `mkOP` build expression nodes.
- `yylex` tokenizes numbers, units, symbols, and operators.
- `eval` recursively evaluates expression trees and checks division by zero.
- `parseexpr` sets parser context (`dot`, `dollar`, `size`), invokes `yyparse`, and returns either an error string or result.

Role:
- Shared by `prep/edit.c` commands for partition start/end expressions.
