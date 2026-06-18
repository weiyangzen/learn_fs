# File Research: sources/os/bsd/netbsd-src/lib/libcurses/cur_hash.c

Read completely: 87 lines.

This file implements line hashing. `__hash_more` is the PJW hash from the Dragon Book, taking an existing hash seed and a byte span. `__hash_line` hashes an array of `__LDATA` cells.

In wide builds, `__hash_line` hashes each cell's base character, attributes, and every nonspacing character in its `nsp` list. In narrow builds, it hashes the raw `__LDATA` memory for the full line.

Important interactions: used by refresh optimization to detect changed lines. It depends on `__LDATA` having stable representation in narrow builds; `curses_private.h` explicitly warns against padding in `__LDATA`.

Reliability notes: wide hashing omits `cflags` and `wcols`, so visual state represented only by those fields is not part of the hash.
