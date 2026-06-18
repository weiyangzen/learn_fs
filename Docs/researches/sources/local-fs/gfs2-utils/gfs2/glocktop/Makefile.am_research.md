# File Research: sources/local-fs/gfs2-utils/gfs2/glocktop/Makefile.am

This Automake fragment builds the `glocktop` utility as an sbin program from `glocktop.c`.

Build configuration:
- `sbin_PROGRAMS = glocktop`
- `glocktop_SOURCES = glocktop.c`
- Adds ncurses flags through `glocktop_CFLAGS`.
- Defines `_GNU_SOURCE` via `glocktop_CPPFLAGS`.
- Links against `gfs2/libgfs2/libgfs2.la`, ncurses libraries, and uuid libraries.

The file is narrow build glue. Its main integration point is ensuring `glocktop` has libgfs2 and ncurses support available at link time.
