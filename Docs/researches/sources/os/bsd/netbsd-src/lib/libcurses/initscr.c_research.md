# File Research: sources/os/bsd/netbsd-src/lib/libcurses/initscr.c

Implements `initscr()`, the traditional default-screen initializer.

It chooses `TERM` unless `My_term` or missing environment forces `Def_term`, calls `newterm`, exits with a diagnostic on failure per POSIX expectations, installs the returned screen with `set_term`, refreshes `curscr`, touches ripoff windows, and returns `stdscr`.
