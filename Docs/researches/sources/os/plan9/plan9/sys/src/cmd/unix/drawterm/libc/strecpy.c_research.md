# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strecpy.c

This file copies a C string into a bounded destination.

Key behavior:
- `strecpy` copies from `from` into `[to, e)` and NUL-terminates when possible.

Important details:
- Returns a pointer to the final NUL/end position.
