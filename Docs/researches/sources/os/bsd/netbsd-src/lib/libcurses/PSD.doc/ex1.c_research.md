# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/ex1.c

Read completely: 100 lines.

Historical curses documentation example embedded as a C listing with roff-style leading comments. It initializes curses, installs a SIGINT cleanup handler, switches to cbreak/noecho, replaces `stdscr` with a 10x20 window, enables flushing and scrolling, and loops on `getchar()`.

Commands are minimal: `q` quits, `s` enters standout mode, `e` exits standout mode, `r` forces refresh from `curscr`, and any other character is added to the window. `quit()` erases, refreshes, calls `endwin()`, deletes `curscr`/`stdscr`, prints a newline, and exits.

It demonstrates elementary curses lifecycle and output control. It is K&R-era code with implicit `main`, old `crmode()`, and no modern prototypes.
