# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fprint.c

This file implements formatted output to an fd.

Key behavior:
- `fprint` wraps `vfprint` with varargs.

Important details:
- Plan 9 equivalent of `fprintf` for integer file descriptors.
