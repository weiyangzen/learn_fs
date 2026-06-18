# File Research: sources/os/bsd/netbsd-src/lib/libcurses/addwstr.c

Read completely: 168 lines.

Implements wide-string add APIs for `wchar_t` strings: `addwstr`, `waddwstr`, `addnwstr`, movement variants, and core `waddnwstr()`.

The core validates the window, rejects `n < -1`, computes the number of wide characters to emit from `n` or `wcslen()`, converts each `wchar_t` into a single-element `cchar_t` with the window’s current wide attributes via `setcchar()`, and delegates each character to `wadd_wch()`.

This means all cursor movement, line wrapping, scrolling, nonspacing behavior, and dirty tracking are handled by the shared `wadd_wch()`/`_cursesi_addwchar()` path. It returns `ERR` on invalid movement, conversion failure, or add failure.
