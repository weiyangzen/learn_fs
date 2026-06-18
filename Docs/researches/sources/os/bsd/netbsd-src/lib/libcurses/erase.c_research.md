# File Research: sources/os/bsd/netbsd-src/lib/libcurses/erase.c

Read completely: 109 lines.

This file implements `erase` and `werase`, clearing an entire window and moving the cursor to the origin.

`werase` validates the window, chooses background character/attributes, iterates every cell, and only rewrites cells that satisfy `__NEED_ERASE`. Rewritten cells become background cells, lose continuation state, preserve `__ALTCHARSET`, copy background nonspacing characters in wide builds, and set `wcols = 1`. The whole window is touched to handle overlaps, then `wmove(win, 0, 0)` resets the cursor.

Important interactions: shared erase semantics with `clrtobot` and `clrtoeol`; depends on `_cursesi_copy_nsp`, `__touchwin`, and `wmove`.

Reliability notes: wide erasure can return `ERR` after partially clearing the window if copying nonspacing data fails.
