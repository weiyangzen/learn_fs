# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vseprint.c

This file formats a `va_list` into a bounded byte buffer ending at a pointer.

Key behavior:
- `vseprint` initializes a bounded `Fmt`, dispatches formatting, terminates output, and returns the end pointer.

Important details:
- Pointer-end counterpart to `vsnprint`.
