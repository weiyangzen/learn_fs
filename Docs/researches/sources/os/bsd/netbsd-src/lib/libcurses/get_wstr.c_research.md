# File Research: sources/os/bsd/netbsd-src/lib/libcurses/get_wstr.c

Read completely: 256 lines.

This file implements wide-string input wrappers and editing behavior: `getn_wstr`, unsafe `get_wstr`, `mvgetn_wstr`, unsafe `mvget_wstr`, `mvwgetn_wstr`, unsafe `mvwget_wstr`, unsafe `wget_wstr`, `wgetn_wstr`, and internal `__wgetn_wstr`.

Bounded APIs reject `n < 1`, and for `n == 1` write an empty string and return `ERR`. The unbounded APIs emit link-time warnings through `__warn_references`. `__wgetn_wstr` reads wide characters with `wget_wch` until newline, carriage return, or error; supports erase, backspace, left, and kill characters; erases display cells using the window background character wrapped in a `cchar_t`; ignores function-key values after removing their echoed display; and always null-terminates the result.

Important interactions: depends on `wget_wch`, `erasewchar`, `killwchar`, `setcchar`, `mvwadd_wch`, `wmove`, and line touch behavior.

Reliability notes: editing assumes the cursor positions created by `wget_wch` echoing match the cleanup coordinates here. Some cleanup paths address `win->curx - 1` or `win->curx - 2`, so correctness depends on the preceding echo behavior and current cursor state.
