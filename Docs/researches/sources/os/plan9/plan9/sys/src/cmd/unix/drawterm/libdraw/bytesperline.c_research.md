# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/bytesperline.c

Computes storage width for image scan lines.

Key functions:
- `unitsperline`: shared implementation for rounding rectangle pixel spans to a target unit size.
- `wordsperline`: returns scan-line length in `ulong` units.
- `bytesperline`: returns scan-line length in bytes.

Important behavior:
- Handles negative `r.min.x` carefully by making the division domain positive before rounding.
- Aborts if called with an invalid image depth outside `1..32`.
