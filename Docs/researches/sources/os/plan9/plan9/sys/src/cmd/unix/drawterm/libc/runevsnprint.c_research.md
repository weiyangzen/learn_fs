# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevsnprint.c

This file formats into a fixed-size rune buffer using a `va_list`.

Key behavior:
- `runevsnprint` initializes a bounded rune `Fmt`, dispatches formatting, and NUL-terminates.

Important details:
- Returns formatted rune count or error.
