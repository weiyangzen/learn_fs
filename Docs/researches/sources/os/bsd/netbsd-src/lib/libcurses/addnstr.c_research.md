# File Research: sources/os/bsd/netbsd-src/lib/libcurses/addnstr.c

Read completely: 173 lines.

Implements narrow string add APIs: `addstr`, `waddstr`, `addnstr`, `mvaddstr`, `mvwaddstr`, `mvaddnstr`, `mvwaddnstr`, and core `waddnstr()`.

Wrappers delegate through `stdscr` or movement to `waddnstr()`. The core computes length using NetBSD/ncurses-compatible semantics: `n >= 0` means at most `n` bytes, while negative means the whole C string. It then calls `waddbytes()` to perform actual output with normal character interpretation.

This file is API glue; wrapping, scrolling, tabs, newline handling, and dirty marking are handled by `addbytes.c`.
