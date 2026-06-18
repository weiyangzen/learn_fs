# File Research: sources/os/plan9/9front/sys/src/cmd/db/input.c

Purpose: Input buffering and token mechanics for `db`.

Key behavior:
- Maintains a UTF `Rune line[LINSIZ]`, current pointer `lp`, `peekc`, `lastc`, and `eof`.
- `readrune()` reads UTF-8 from fd one byte at a time until a full rune is available.
- `readchar()` reads from `peekc`, from the current in-memory line, or fills a new line from `infile`; backslash-newline joins lines.
- `rdc()` skips spaces/tabs.
- `reread()` pushes back the last character.
- `clrinp()` clears input and flushes output.
- `nextchar()` returns the next non-space char unless at end of command.
- `quotchar()` handles quoted character constants.
- `getformat()` reads a format string through end-of-line/semicolon, preserving quoted sections.
- `isfileref()` looks ahead to distinguish `filename:line` from `:` process commands.

Notable details:
- Interrupt handling uses `mkfault` to abort the current input read through `error()`.
