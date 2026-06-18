# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtvprint.c

This file formats varargs into an existing `Fmt`.

Key behavior:
- `fmtvprint` copies the `va_list`, calls `__fmtdispatch`, and returns the number of bytes/runes written.

Important details:
- Central bridge between public vararg wrappers and formatter dispatch.
