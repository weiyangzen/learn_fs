# File Research: sources/os/bsd/netbsd-src/lib/libcurses/border.c

Read completely: 625 lines.

This file draws borders for narrow and wide curses windows. It implements `border`, `wborder`, `border_set`, and `wborder_set`. `box.c` delegates to these routines.

In non-wide builds, `wborder` supplies ACS defaults for omitted characters, merges each border character with current window and background attributes, writes left/right sides, top/bottom lines, and corners, then touches the full window. It avoids writing corners for a full-screen scrolling window, matching the historical bottom-right scroll hazard.

In wide builds, `wborder` converts `chtype` values into `cchar_t` values or WACS defaults, then delegates to `wborder_set`. `wborder_set` copies or defaults all eight border glyphs, merges attributes, handles display widths with `wcwidth`, writes continuation cells using negative `wcols`, clears overlapping partial wide characters back to background cells, manages nonspacing lists per cell, and handles corners with separate width calculations.

Important interactions: uses ACS/WACS tables from `curses.h`, `WINDOW` cell layout from `curses_private.h`, `__cursesi_chtype_to_cchar`, `_cursesi_copy_nsp`, `__touchwin`, and background fields `bch`, `battr`, and `bnsp`.

Reliability notes: wide `wborder_set` performs many per-cell allocations for nonspacing characters; allocation failure returns `ERR` after earlier cells may already have been modified. The function repeatedly frees existing nonspacing lists manually, so ownership invariants of `__LDATA.nsp` are critical.
