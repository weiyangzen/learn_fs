# File Research: sources/os/bsd/netbsd-src/lib/libcurses/setterm.c

Implements terminal capability setup: `setterm`, `_cursesi_setterm`, `_cursesi_resetterm`, and `set_tabsize`.

`_cursesi_setterm` loads terminfo, falls back to `dumb`, applies filter mode capability removal, initializes `LINES`, `COLS`, `ESCDELAY`, `TABSIZE`, padding, quick-change eligibility, and attribute/color conflict masks. Helpers detect reset capabilities that imply `ESC[m` or ACS reset behavior after stripping delay specs. `_cursesi_resetterm` copies screen-local terminal settings back to global curses state and calls `set_curterm`.
