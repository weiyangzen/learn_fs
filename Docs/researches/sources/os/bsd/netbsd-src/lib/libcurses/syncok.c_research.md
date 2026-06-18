# File Research: sources/os/bsd/netbsd-src/lib/libcurses/syncok.c

Implements `syncok(WINDOW *win, bool bf)`.

It toggles the `__SYNCOK` flag, used by synchronization helpers to propagate changes from subwindows or windows to related ancestors/descendants.
