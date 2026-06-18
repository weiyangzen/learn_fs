# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevsmprint.c

This file allocates formatted rune strings using a `va_list`.

Key behavior:
- `runefmtstrinit` initializes a growable rune formatter.
- `runeFmtStrFlush` grows the buffer when full.
- `runevsmprint` formats, flushes, and returns the allocated rune string.

Important details:
- Rune counterpart to `vsmprint`.
