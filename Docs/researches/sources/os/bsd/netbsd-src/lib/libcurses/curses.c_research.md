# File Research: sources/os/bsd/netbsd-src/lib/libcurses/curses.c

Read completely: 214 lines.

This file defines core libcurses global variables and wide-cell helper functions. Globals include public `curscr`, `stdscr`, `COLS`, `LINES`, `ESCDELAY`, `TABSIZE`, `COLORS`, `COLOR_PAIRS`, `Def_term`, and private state such as `__echoit`, `__rawmode`, `__pfast`, `__noqch`, `__virtscr`, and `_cursesi_screen`.

`_cursesi_celleq` compares two cells by character and attributes, and under wide support also compares continuation flags and nonspacing-character lists. `_cursesi_copy_wchar` copies a full wide cell. `_cursesi_copy_nsp` copies a source nonspacing list into an existing cell list, allocating or freeing nodes as needed. `__cursesi_free_nsp` frees one nonspacing list, and `__cursesi_win_free_nsp` frees all per-cell nonspacing lists in a window.

Important interactions: background, border, erase, delete, file I/O, and refresh-related code rely on these helpers for complex character ownership and equality.

Reliability notes: `_cursesi_copy_nsp` appears fragile when copying a non-empty source list into a destination cell with `ch->nsp == NULL`: `pnp` starts null, but the allocation branch assigns through `pnp->next`. Callers that copy background nonspacing data into empty cells depend on this path.
