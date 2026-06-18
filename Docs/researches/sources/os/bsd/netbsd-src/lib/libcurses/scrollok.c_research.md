# File Research: sources/os/bsd/netbsd-src/lib/libcurses/scrollok.c

Implements `scrollok(WINDOW *win, bool bf)`.

It toggles the `__SCROLLOK` flag that allows `scroll`, newline insertion, and bottom-edge writes to scroll the window instead of failing.
