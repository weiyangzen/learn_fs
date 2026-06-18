# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/snprint.c

This file formats into a fixed-length byte buffer.

Key behavior:
- `snprint` wraps `vsnprint` with varargs.

Important details:
- Plan 9 equivalent of `snprintf`.
