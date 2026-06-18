# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrecpy.c

This file copies rune strings into a bounded destination.

Key behavior:
- `runestrecpy` copies from `s2` into `[s1, es1)` and NUL-terminates when space allows.

Important details:
- Returns a pointer to the final NUL or end position.
