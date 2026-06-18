# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/input.c

Input-source and macro expansion engine for `eqn`.

Key behavior:
- Maintains a stack of sources: file, macro, string, single-character pushback, and free-on-pop string.
- Expands macro arguments `$1..$n`.
- `dodef()` collects macro call arguments and switches input to the definition body.
- `input()` reads from current source, tracks file line numbers, closes included files on EOF, and records error context.
- `unput()` implements pushback through a character source.
- Error reporting prints command/file/line context and injects a safe `.EN`.

Filesystem relevance:
- Reads included input files opened by the lexer and closes them on EOF.
