# File Research: sources/os/bsd/netbsd-src/lib/libcurses/getstr.c

Read completely: 262 lines.

This file implements narrow string input: `getnstr`, unsafe `getstr`, `mvgetnstr`, unsafe `mvgetstr`, `mvwgetnstr`, unsafe `mvwgetstr`, unsafe `wgetstr`, `wgetnstr`, and internal `__wgetnstr`.

Bounded APIs reject `n < 1`, and for `n == 1` store an empty string and return `ERR`. Unbounded APIs emit link-time unsafe-use warnings. `__wgetnstr` reads through `wgetch` until newline, carriage return, or `ERR`, supports erase, backspace, left, and kill characters, removes echoed key/control display from the window, ignores function keys after cleaning their display, tracks a remaining character budget, and null-terminates the output.

Important interactions: depends on `wgetch`, terminal erase/kill characters, `mvwaddch`, `wmove`, `__touchline`, and cursor behavior from input echoing.

Reliability notes: unbounded APIs are explicitly unsafe. Editing is byte-oriented and screen cleanup is based on how `wgetch` displays control/key sequences.
