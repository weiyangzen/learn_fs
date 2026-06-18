# File Research: sources/os/bsd/netbsd-src/lib/libcurses/clear.c

Read completely: 73 lines.

This file implements `clear` and `wclear`. `clear` delegates to `_cursesi_screen->stdscr` when macro mode is disabled. `wclear` validates the window, calls `werase`, and sets the `__CLEAROK` flag so the next refresh performs a full clear.

Important interactions: uses `werase` from `erase.c` and the window flag definitions in `curses_private.h`.

Reliability notes: `clear()` assumes `_cursesi_screen` is initialized.
