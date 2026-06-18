# File Research: sources/os/bsd/netbsd-src/lib/libcurses/inchstr.c

Implements `chtype` array extraction from the current line: `inchstr`, `inchnstr`, movement variants, `winchstr`, and `winchnstr`.

Unbounded variants are marked unsafe. `winchnstr` copies from cursor to EOL or up to `n - 1` entries, appends a zero element, and preserves attributes while masking internal wide-character ACS flags under `HAVE_WCHAR`.
