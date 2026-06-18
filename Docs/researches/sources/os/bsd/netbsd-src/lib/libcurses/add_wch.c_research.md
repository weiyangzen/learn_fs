# File Research: sources/os/bsd/netbsd-src/lib/libcurses/add_wch.c

Read completely: 114 lines.

Implements the wide-character single-cell add wrappers: `add_wch()`, `mvadd_wch()`, `mvwadd_wch()`, and `wadd_wch()`.

The stdscr and move variants delegate to `wadd_wch()` after optional `wmove()`. `wadd_wch()` validates the window, fetches the current line pointer, and calls the shared internal `_cursesi_addwchar()` with pointers to the window cursor coordinates and `char_interp=1`.

This file is mostly API plumbing. The actual complex behavior for tabs, newlines, nonspacing characters, wide-width continuation cells, dirty ranges, wrapping, and scrolling lives in `addbytes.c`.
