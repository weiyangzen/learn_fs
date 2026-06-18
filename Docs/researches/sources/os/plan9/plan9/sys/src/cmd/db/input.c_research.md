# File Research: sources/os/plan9/plan9/sys/src/cmd/db/input.c

Input buffering and character/rune reading for Plan 9 `db`.

Key responsibilities:
- Maintains global input line buffer `line`, rune pointer `lp`, `peekc`, `lastc`, and `eof`.
- `eol()` recognizes newline and semicolon as command terminators.
- `rdc()` reads next non-space/tab character.
- `reread()` pushes back one character through `peekc`.
- `clrinp()` flushes output and resets input pointer/peek char.
- `readrune()` reads one UTF rune from a file descriptor.
- `readchar()` reads from current line buffer or fills it from `infile`, supporting backslash-newline continuation and interrupt faults.
- `nextchar()` returns next command argument char or 0 at EOL.
- `quotchar()` reads quoted character literal content.
- `getformat()` collects an examine format string, respecting quoted substrings.
- `isfileref()` looks ahead to detect `filename:digits` forms so expression parsing can treat them as file locations.

Important interactions:
- Used by `command.c` and `expr.c`.
- `mkfault` interrupts force `error(0)` during input fill.

Research notes:
- Line input is UTF-aware through `Rune` storage and `runetochar` conversion in callers.
- `getformat()` steps `lp--` after reading terminator so the command loop can see it.
