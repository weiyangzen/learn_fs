# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtfdflush.c

This file provides an fd flush callback for `Fmt`.

Key behavior:
- `__fmtFdFlush` writes pending bytes to the fd stored in the formatter.

Important details:
- This is a compatibility/internal variant used by the formatting layer.
