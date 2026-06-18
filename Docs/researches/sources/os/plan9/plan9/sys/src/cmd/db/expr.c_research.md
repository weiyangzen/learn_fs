# File Research: sources/os/plan9/plan9/sys/src/cmd/db/expr.c

Expression parser for the Plan 9 `db` debugger.

Key responsibilities:
- Parses expressions using recursive routines:
  - `expr()` handles dyadic operators.
  - `term()` handles unary operators and parenthesized expressions.
  - `item()` handles symbols, locals, numbers, dot, registers, file references, character constants, and ditto.
- Supported dyadic operators include `+`, `-`, `#` rounding, `*`, `%`, `&`, `|`.
- Supported unary operators include memory indirection through core map (`*`), symbol map (`@`), negation, bitwise complement, and parentheses.
- `item()` resolves:
  - `file:line` references via `file2pc`.
  - global symbols via `lookup`.
  - local symbols via `localaddr`.
  - current function locals from current PC.
  - `<register` via `rget`.
  - quoted character constants.
- `getnum()` parses numeric constants with base prefixes:
  - `#` for hex
  - `0x` hex
  - `0t` decimal
  - `0o` octal
  - default decimal or leading-zero octal.
- `readsym()` and `readfname()` collect UTF-aware symbol/file tokens.
- `symchar()` defines symbol character rules.
- `round()` implements `#` operator rounding.

Important interactions:
- Uses `lastc`/`readchar()`/`reread()` from `input.c`.
- Uses libmach symbol/local APIs and register map callbacks.

Research notes:
- Floating literals are accepted if a dot appears during number parsing; they are converted to a `float` bit pattern stored in `WORD`.
- Division by zero is handled specially: nonzero numerator yields 1, zero numerator yields 0.
