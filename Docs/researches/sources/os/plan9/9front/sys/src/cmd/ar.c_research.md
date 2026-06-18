# File Research: sources/os/plan9/9front/sys/src/cmd/ar.c

Portable ASCII-format archive tool implementing Plan 9 `ar` operations: replace/update, delete, extract, table, print, move, and quick append.

Important behavior:
- Uses up to three logical temp streams: members before pivot, moved/inserted members, and members after pivot.
- Temp streams are kept in memory as member chains and spill to disk when allocation fails.
- Reads and writes archive headers field-by-field using the `HEADER_IO` macro.
- Regenerates `__.SYMDEF` for homogeneous object archives and detects duplicate text symbols.
- Supports pivot insertion with `a`, `b`, and `i`, verbose output, update-if-newer, and preserve-time extraction.

Key dependencies are Plan 9 `bio`, `ar.h`, and `mach` object-symbol parsing.
