# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/print.c

This file implements formatted output to stdout.

Key behavior:
- `print` wraps `vfprint(1, ...)`.

Important details:
- Plan 9 equivalent of printing to fd 1.
