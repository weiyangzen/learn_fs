# File Research: sources/os/plan9/plan9/sys/src/cmd/proof/main.c

Purpose: Program entry point and input buffering layer for the interactive `proof` troff previewer.

Key behavior:
- Parses options for map file, font directory, debug, magnification, tracking, x/y offsets, and number of views.
- Opens optional input file on stdin.
- Initializes Bio, loads font map file, initializes font positions, opens screen, clears screen, and starts `readpage`.
- Implements a circular input buffer allowing recent input to be rewound.
- Provides `getc`, `getrune`, `ungetc`, `offsetc`, `seekc`, and `rdlinec`.

Dependencies and integration:
- Uses Plan 9 draw/event and `proof.h`.
- `track` mode is used by screen event loop to detect file modification.

Risks and notes:
- Ring buffer is fixed at 100000 bytes, typically enough for several pages.
- `seekc` can only rewind within buffered data.
- `strncpy` into fixed arrays may leave unterminated strings if arguments are too long.
