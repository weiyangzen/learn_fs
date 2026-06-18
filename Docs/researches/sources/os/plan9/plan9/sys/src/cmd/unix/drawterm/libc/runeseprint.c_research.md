# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runeseprint.c

This file formats into a bounded rune buffer ending at a pointer.

Key behavior:
- `runeseprint` wraps `runevseprint` with varargs.

Important details:
- Returns the end pointer after formatted output.
