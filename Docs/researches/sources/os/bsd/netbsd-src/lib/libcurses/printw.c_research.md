# File Research: sources/os/bsd/netbsd-src/lib/libcurses/printw.c

Implements formatted output APIs: `printw`, `wprintw`, movement variants, `vw_printw`, and alias `vwprintw`.

`vw_printw` formats into a per-window `open_memstream` buffer, rewinding it for reuse, flushes the stream, then sends exactly the formatted byte count to `waddnstr`. It returns `OK` on zero-length output and `ERR` on formatting or stream failures.
