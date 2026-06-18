# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runefmtstr.c

This file finalizes dynamically allocated rune-string formatting.

Key behavior:
- `runefmtstrflush` terminates and returns the accumulated `Rune*`.

Important details:
- Rune counterpart to `fmtstrflush`.
