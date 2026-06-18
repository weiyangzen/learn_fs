# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vsnprint.c

This file formats a `va_list` into a fixed-size byte buffer.

Key behavior:
- `vsnprint` initializes a bounded `Fmt`, dispatches formatting, and NUL-terminates.

Important details:
- Returns formatted byte count or error.
