# File Research: sources/os/bsd/netbsd-src/lib/libcurses/immedok.c

Implements `immedok(WINDOW *win, bool bf)`, the curses switch that marks a window for immediate refresh after changes.

The function is a small state mutator over `WINDOW.flags`: it sets or clears `__IMMEDOK`, returning `ERR` for `NULL` and `OK` otherwise. The actual refresh-on-change behavior is consumed elsewhere through the private `__IMMEDOK` flag.
