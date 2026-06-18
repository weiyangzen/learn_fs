# File Research: sources/os/bsd/netbsd-src/lib/libcurses/screen.c

Implements screen lifecycle and switching: `filter`, `set_term`, `newterm`, `delscreen`, and internal `__delscreen`.

`newterm` allocates and initializes `SCREEN`, termios state, terminal capabilities, `curscr`, `__virtscr`, soft labels, ripoff windows, `stdscr`, getch/ACS/WACS state, and signal handlers, then starts terminal mode. `set_term` saves globals from the old screen, restores globals from the new screen, resets terminal/ACS state, and binds `curscr`, `stdscr`, and `__virtscr`. Destruction frees terminfo, windows, keymaps, soft labels, buffers, and unget storage.
