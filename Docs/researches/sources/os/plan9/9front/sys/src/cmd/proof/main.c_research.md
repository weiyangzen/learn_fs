# File Research: sources/os/plan9/9front/sys/src/cmd/proof/main.c

Entry point and input buffering layer for `proof`. It parses UI/font/magnification/map options, opens the input file or stdin, loads map/fonts, initializes the screen, and starts page reading. It also implements a circular input buffer so the viewer can seek backward within recently read troff output.

Key behavior:
- Options: map file, font directory, debug, magnification, file tracking, x/y offsets, and number of views.
- `getc`, `getrune`, `ungetc`, `seekc`, `offsetc`, and `rdlinec` provide buffered byte/rune/line access.
- `track` mode watches input file modification time via screen event loop.

Integration points:
- Calls `readmapfile`, `loadfontname`, `mapscreen`, `clearscreen`, `readpage`.
- Shares buffer functions declared in `proof.h`.

Risks:
- Circular buffer is fixed at 100000 bytes; seeking older pages can fail.
- `strncpy(libfont, ...)` may leave `libfont` unterminated if option is too long.
