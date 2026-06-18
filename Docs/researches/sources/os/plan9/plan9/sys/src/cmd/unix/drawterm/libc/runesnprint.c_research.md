# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesnprint.c

This file formats into a fixed-length rune buffer.

Key behavior:
- `runesnprint` wraps `runevsnprint` with varargs.

Important details:
- Returns formatted rune count.
