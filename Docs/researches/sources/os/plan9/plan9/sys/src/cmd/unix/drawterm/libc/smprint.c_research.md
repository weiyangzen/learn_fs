# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/smprint.c

This file allocates formatted byte strings.

Key behavior:
- `smprint` wraps `vsmprint` with varargs.

Important details:
- Caller owns the returned allocated buffer.
