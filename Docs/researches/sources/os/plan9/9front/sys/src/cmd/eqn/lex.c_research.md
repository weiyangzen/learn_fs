# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/lex.c

This file is the eqn lexer and directive processor. It turns input into grammar tokens, expands definitions, handles quoted strings, recognizes keywords, and processes top-level eqn directives.

Key responsibilities:
- Skips whitespace and maps `~` to space and `^` to thin space.
- Reads quoted text into `token` and returns `QTEXT`.
- Reads unquoted tokens with `getstr`.
- Expands definitions from `deftbl`, including macros with arguments.
- Recognizes keywords through `keytbl`.
- Processes `define`, `ifdef`, `delim`, `gsize`, `gfont`, `include`, and `space`.
- Handles inline equation termination via `righteq`.

Important implementation notes:
- `define` can tune special floating parameters if the name is in `ftunetbl`.
- `include` opens a file, pushes it onto the input stack, and emits `.lf`.
- `delim off` is represented by setting both delimiter chars to `'\0'`.
