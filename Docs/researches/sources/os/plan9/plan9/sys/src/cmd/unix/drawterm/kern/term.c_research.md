# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/term.c

This file implements a tiny graphical console renderer for drawterm kernel messages.

Key behavior:
- `terminit` initializes font, colors, cursor, and screen window bounds.
- `screenputc` renders characters, handles newline, tab, backspace, carriage return, and scrolls as needed.
- `termscreenputs` writes strings while holding the draw lock.
- `addflush`/`screenflush` accumulate and flush dirty rectangles.

Important details:
- Uses `Memimage`, `memimagedraw`, `memimagestring`, and `flushmemscreen`.
- The terminal window is derived from the current screen rectangle with small margins.
- Output is white background with black text.
