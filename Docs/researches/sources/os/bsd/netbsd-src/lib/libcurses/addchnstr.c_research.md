# File Research: sources/os/bsd/netbsd-src/lib/libcurses/addchnstr.c

Read completely: 186 lines.

Implements `chtype` string add APIs: `addchstr`, `waddchstr`, `addchnstr`, movement variants, and core `waddchnstr()`.

The core function computes the number of characters to write from `n` or NUL termination, truncates to the remaining columns on the current line, and does not wrap, matching SUSv2 addchnstr behavior. It groups runs with the same attribute into temporary byte buffers and calls `_cursesi_waddbytes()` with `char_interp=0`, so control characters are written as data rather than interpreted.

It saves and restores the original cursor position after writing. It allocates a temporary `len + 1` buffer; allocation failure or lower-level add failure returns `ERR`.
