# File Research: sources/os/bsd/netbsd-src/lib/libcurses/in_wch.c

Implements wide-character cell extraction APIs: `in_wch`, `mvin_wch`, `mvwin_wch`, and `win_wch`.

The public variants delegate to `stdscr` or move first with `wmove`. `win_wch` reads the current `__LDATA` cell, backs up from a continuation cell using negative `wcols`, and fills a `cchar_t` with the base wide character, attributes, and linked non-spacing characters from `nschar_t`.
