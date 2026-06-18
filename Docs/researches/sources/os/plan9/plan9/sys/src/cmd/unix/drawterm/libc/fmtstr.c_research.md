# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtstr.c

This file finalizes a dynamically allocated string formatter.

Key behavior:
- `fmtstrflush` terminates and returns the accumulated string.

Important details:
- Used by `vsmprint`/`smprint`.
