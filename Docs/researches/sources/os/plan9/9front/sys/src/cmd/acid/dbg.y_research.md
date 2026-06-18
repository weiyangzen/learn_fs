# File Research: sources/os/plan9/9front/sys/src/cmd/acid/dbg.y

Yacc grammar for the Acid debugger language.

Key responsibilities:
- Defines token/value types for identifiers, constants, floats, strings, statements, and expressions.
- Parses top-level statements, function definitions/deletions, and complex type definitions.
- Parses statements: blocks, if/else, loop ranges, while, return, local declarations, and complex declarations.
- Parses expressions with precedence for assignment, formatting, logic, bitwise, comparison, shifts, arithmetic, casts, indexing, field selection, calls, builtins, list literals, constants, strings, eval, head/tail/append/delete, and whatis.
- Executes top-level statements immediately through `execrec()`.

Important behavior:
- Function definitions store an AST `OLIST(args, body)` in the symbol’s `proc`.
- `fn name` without body clears a function.
- `builtin name(args)` forces lookup of a registered builtin.
- Newlines in interactive mode are converted by the lexer to semicolon-like statement terminators.

Dependencies:
- Uses `Node` allocation helpers, `defcomplex()`, `execrec()`, and lexer tokens from `lex.c`.

Notable risks:
- Grammar builds ASTs directly during parse; parse-time side effects for top-level execution affect interactive behavior.
