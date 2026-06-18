# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtod.c

This file implements decimal string to double conversion for the formatting library.

Key behavior:
- `fmtstrtod` parses sign, decimal digits, exponent, `nan`, and `inf`.
- Helper routines normalize decimal digits, compare against floating representation, and multiply/divide decimal buffers.
- Handles rounding and range errors.

Important details:
- Uses custom arbitrary decimal adjustment rather than delegating to host `strtod`.
- Exposes the Plan 9 formatting-library name `fmtstrtod`.
