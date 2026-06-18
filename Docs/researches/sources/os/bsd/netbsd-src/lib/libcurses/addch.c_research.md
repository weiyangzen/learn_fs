# File Research: sources/os/bsd/netbsd-src/lib/libcurses/addch.c

Read completely: 129 lines.

Implements narrow `addch` APIs and the low-level `__waddch()` bridge. When macros are not used, it defines `addch()`, `mvaddch()`, and `mvwaddch()` as wrappers around `waddch()` with optional movement.

With `HAVE_WCHAR`, `waddch()` converts `chtype` to `cchar_t` using `__cursesi_chtype_to_cchar()` and delegates to `wadd_wch()`, unifying narrow and wide paths. Without wide support, it fills an `__LDATA` cell with character and attributes and calls `__waddch()`.

`__waddch()` turns the character into a one-byte string and calls `_cursesi_waddbytes()` with interpretation enabled. This file is mostly compatibility/API layering over `addbytes.c`.
