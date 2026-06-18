# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/cols.c

This file manages Acme columns and windows within columns.

Key behavior:
- `colinit()` creates a column tag with commands `New Cut Paste Snarf Sort Zerox Delcol`.
- `coladd()` inserts or creates a window, splitting existing window space if needed.
- `colclose()` removes a window and resizes neighbors to fill the gap.
- `colresize()` resizes all contained windows proportionally.
- `colsort()` sorts windows by body file name.
- `colgrow()` grows a selected window, makes it full size, packs siblings, or normalizes sizing.
- `coldragwin()` handles window drag, shuffle, grow, and cross-column moves.
- `colwhich()` maps mouse points to column tag, window tag, or body text.
- `colclean()` checks whether all windows are clean.

Important details:
- `c->safe` tracks whether all windows are visible or a full-size window is obscuring others.
- Window movement preserves/restores mouse placement heuristically.
- Window geometry is quantized by tag/body font heights.

Filesystem relevance:
- Indirect UI layer around file-backed `Window`/`Text` objects.
