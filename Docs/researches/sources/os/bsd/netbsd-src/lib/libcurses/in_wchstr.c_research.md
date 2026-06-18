# File Research: sources/os/bsd/netbsd-src/lib/libcurses/in_wchstr.c

Implements wide complex-character string extraction: `in_wchstr`, `in_wchnstr`, movement variants, `win_wchstr`, and `win_wchnstr`.

The unsafe unbounded functions carry `__warn_references`. `win_wchnstr` starts at the current cell, normalizes continuation cells to their leading character, copies each complete wide cell into a `cchar_t` array, includes non-spacing character chains, and appends a wide NUL complex character.
