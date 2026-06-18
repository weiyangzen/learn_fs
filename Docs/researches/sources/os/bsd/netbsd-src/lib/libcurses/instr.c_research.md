# File Research: sources/os/bsd/netbsd-src/lib/libcurses/instr.c

Implements narrow string extraction: `instr`, `innstr`, movement variants, `winstr`, and `winnstr`.

Unbounded functions are marked unsafe. `winnstr` copies `__CHARTEXT` bytes from cursor to EOL or up to `n - 1`, appends NUL, returns `OK` for unbounded calls and the copied count for bounded calls. The file explicitly notes it does not yet support multibyte string extraction.
