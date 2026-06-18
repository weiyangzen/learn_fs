# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesmprint.c

This file allocates a formatted rune string.

Key behavior:
- `runesmprint` wraps `runevsmprint` with varargs.

Important details:
- Caller owns the returned allocated buffer.
