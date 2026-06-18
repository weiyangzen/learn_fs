# File Research: sources/os/bsd/netbsd-src/lib/libcurses/line.c

Implements horizontal and vertical line drawing for narrow and wide curses APIs.

The narrow `hline`/`vline` paths delegate to wide `*_set` functions under `HAVE_WCHAR`; otherwise they repeatedly call `mvwaddch` with default ACS line characters when no character is supplied. Wide `whline_set` and `wvline_set` convert defaults to `WACS_HLINE`/`WACS_VLINE`, respect display width, draw with `mvwadd_wch`, restore the original cursor, and sync the window.
