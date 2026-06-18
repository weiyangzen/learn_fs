# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/errfmt.c

This file provides an error-string format conversion.

Key behavior:
- `errfmt` delegates to `__errfmt`.

Important details:
- The active error-string source is implemented in `kern/sysfile.c`.
