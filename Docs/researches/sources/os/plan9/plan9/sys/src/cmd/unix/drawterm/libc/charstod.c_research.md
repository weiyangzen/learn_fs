# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/charstod.c

This file converts a character stream callback into a double.

Key behavior:
- `fmtcharstod` reads characters through a callback, buffers a numeric token, and calls `fmtstrtod`.

Important details:
- Supports the formatting library's float parsing needs.
- Handles sign, decimal point, and exponent scanning before delegating exact conversion.
