# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevseprint.c

This file formats into a bounded rune buffer using a `va_list`.

Key behavior:
- `runevseprint` initializes a rune `Fmt`, dispatches formatting, terminates output, and returns the end pointer.

Important details:
- Pointer-end variant of rune formatted printing.
