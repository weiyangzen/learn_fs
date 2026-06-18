# File Research: sources/os/bsd/netbsd-src/lib/libcurses/deleteln.c

Read completely: 65 lines.

This file implements line deletion wrappers. `deleteln()` deletes one line from `stdscr` by calling `winsdelln(stdscr, -1)`, and `wdeleteln(win)` calls `winsdelln(win, -1)`.

Important interactions: real behavior is implemented in the insert/delete-line code outside this group.

Reliability notes: validation is delegated to `winsdelln`.
