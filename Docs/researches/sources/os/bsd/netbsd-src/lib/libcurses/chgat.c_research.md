# File Research: sources/os/bsd/netbsd-src/lib/libcurses/chgat.c

Read completely: 101 lines.

This file implements attribute changes over a run of cells without changing characters: `chgat`, `mvchgat`, `wchgat`, and `mvwchgat`.

`mvwchgat` validates the window and coordinates, combines requested attributes with `COLOR_PAIR(color)`, clamps negative or oversized counts to the rest of the line, marks the affected line dirty, updates `firstchp`/`lastchp`, and overwrites each target cell's attributes. Wide builds preserve only non-wide attribute bits by replacing `WA_ATTRIBUTES`; narrow builds assign the full attribute value.

Important interactions: depends on `WINDOW` line dirty tracking from `curses_private.h`, `wmove` through movement wrappers, and the public color-pair encoding macros.

Reliability notes: `wchgat(win, ...)` computes `win->cury` and `win->curx` before `mvwchgat` can validate `win`; passing a null window to `wchgat` can dereference null.
