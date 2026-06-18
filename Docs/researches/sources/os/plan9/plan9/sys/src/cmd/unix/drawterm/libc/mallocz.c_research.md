# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/mallocz.c

This file implements Plan 9's `mallocz`.

Key behavior:
- `mallocz` calls `malloc` and zeroes memory only when `clr` is nonzero.

Important details:
- Returns `nil` if allocation fails.
