# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtprint.c

This file prints formatted text into an existing `Fmt`.

Key behavior:
- `fmtprint` wraps `fmtvprint` with varargs.

Important details:
- Useful for custom formatters that append to the current formatter.
