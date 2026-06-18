# File Research: sources/os/bsd/netbsd-src/lib/libcurses/add_wchstr.c

Read completely: 301 lines.

Implements wide complex-character string add APIs: `add_wchstr`, `wadd_wchstr`, `add_wchnstr`, movement variants, and core `wadd_wchnstr()`.

Unlike `wadd_wch()`, this family does not wrap. It writes at most `n` `cchar_t` entries, or the whole NUL-terminated sequence for `n == -1`, truncating at the right edge. It handles writing over the middle of an existing wide character by clearing affected continuation cells or moving to the character start for nonspacing additions.

For spacing characters, it clears old nonspacing lists, writes the base wide char and attributes, adds extra elements as nonspacing nodes, marks continuation cells for multi-column width, and updates dirty ranges. For nonspacing characters, it attaches them to the current cell’s `nsp` list. Allocation failures for nonspacing nodes return `ERR`.
