# File Research: sources/os/bsd/netbsd-src/lib/libcurses/nodelay.c

Implements `nodelay(WINDOW *win, bool bf)`.

It maps nonblocking input to `win->delay = 0` and blocking input to `win->delay = -1`, returning `ERR` for `NULL`. `getch`-side code consumes this delay value.
