# File Research: sources/os/bsd/netbsd-src/lib/libcurses/copywin.c

Read completely: 142 lines.

This file implements `copywin`, copying an intersected rectangle from one window to another. It supports destructive overwrite mode and nondestructive overlay mode.

The function normalizes negative source and destination coordinates, clamps the destination maximum row/column to the intersection of both windows, then iterates source cells and writes destination cells through `wmove` plus `__waddch` in narrow builds or `wadd_wch` in wide builds. Overlay mode skips source cells where `isspace(sp->ch)` is true.

Important interactions: used by higher-level `overlay`/`overwrite` style routines. Wide mode converts each `__LDATA` plus its nonspacing list into a temporary `cchar_t`.

Reliability notes: the wide nonspacing copy loop uses `cc.elements <= CURSES_CCHAR_MAX` while appending into `vals`, which can write one past the fixed array if a cell has the maximum number of nonspacing characters. The return values of `wmove`, `__waddch`, and `wadd_wch` are not checked inside the copy loop.
