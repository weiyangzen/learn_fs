# File Research: sources/os/bsd/netbsd-src/lib/libcurses/cr_put.c

Read completely: 517 lines.

This file implements terminal cursor motion and low-level cursor-position optimization. Public `mvcur` delegates to internal `__mvcur`, which initializes desired and current coordinates and calls `fgoto`.

`fgoto` normalizes positions around terminal width/height, accounts for wraparound, scrolls when the destination is below the screen, chooses between direct `cursor_address` addressing and local motion, and updates `outcol`/`outline`. `plod` estimates and optionally emits local motion using home, lower-left, carriage return, cursor up/down/left/right, tabs, backspace, and, during refresh, already-rendered `curscr` cells. `plodput` supports cost estimation by decrementing `plodcnt` instead of outputting. `tabcol` computes tab stops.

Important interactions: depends on global terminal dimensions and capabilities (`COLS`, `LINES`, `cursor_address`, `cursor_home`, `cursor_down`, `cursor_up`, `tab`, etc.), `curscr` contents, `__cputchar`, and wide output helpers `__cputwchar`/`__cursesi_putnsp`.

Reliability notes: this code assumes `curscr` accurately mirrors the physical screen when using refresh-time plodding. Wide builds refuse to plod from a continuation cell. The code has historical comments about imperfect cost accounting, such as carriage-return capability length not being included.
