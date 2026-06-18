# File Research: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/Makefile

Read completely: 54 lines.

Developer/example Makefile for building curses demonstration programs from `view.c` and `ex1.c`. It builds variants against local NetBSD curses, system curses, and pkgsrc ncurses, with optional `HAVE_WCHAR` and `NCURSES` defines.

Targets include `wcview`, `nwview`, `ccview`, `tcview`, `ncview`, and `ex1`. It hardcodes `gcc`, include/library paths, rpaths, and optional debug `CFLAGS`, so it is a convenience/example Makefile rather than part of the normal NetBSD bsd.lib build.
