# File Research: sources/os/bsd/netbsd-src/lib/libcurses/ins_wstr.c

Implements wide-string insertion APIs: `ins_wstr`, `ins_nwstr`, movement variants, `wins_wstr`, and `wins_nwstr`.

`wins_nwstr` precomputes display width with `wcwidth`, handles backspace, carriage return, newline, tab expansion, and scroll-region constraints, then shifts line cells and inserts each wide character through `_cursesi_addwchar`. It preserves the original cursor position, marks changed regions, clears to EOL across embedded newlines, scrolls when allowed, and syncs parent windows.
