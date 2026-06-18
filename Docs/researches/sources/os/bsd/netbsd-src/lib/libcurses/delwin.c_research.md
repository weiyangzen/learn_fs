# File Research: sources/os/bsd/netbsd-src/lib/libcurses/delwin.c

Read completely: 118 lines.

This file implements `delwin`, releasing a `WINDOW` and its associated resources. It treats `NULL` as success. Wide builds first free all per-cell nonspacing lists.

For original windows (`orig == NULL`), it frees the window cell storage, recursively deletes subwindows from the circular subwindow list, and removes the window from the screen's window list. For subwindows, it unlinks the subwindow from its original window's circular list without freeing shared cell storage. It then frees line storage, line pointer arrays, formatted output file/buffer state, clears matching `_cursesi_screen` pointers, and frees the window object.

Important interactions: depends on subwindow list invariants maintained by window creation and `__id_subwins`. It updates `_cursesi_screen->curscr`, `stdscr`, and `__virtscr` if the deleted window matches.

Reliability notes: recursively deleting subwindows while walking the circular list depends on capturing `np = wp->nextp` before deletion. External references to deleted subwindows become invalid.
