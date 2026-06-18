# File Research: sources/os/bsd/netbsd-src/lib/libcurses/id_subwins.c

Read completely: 60 lines.

This file implements internal `__id_subwins(WINDOW *orig)`, resynchronizing subwindow line pointers after the original window's line storage changes.

It walks the original window's circular subwindow list, computes each subwindow's y offset from the original, and repoints each subwindow line to the corresponding slice of the original line using `win->ch_off`.

Important interactions: used by resize or insert/delete line operations that can move original window line storage. It relies on subwindow circular-list invariants.

Reliability notes: no null checks are performed; callers must pass an original window with a valid circular subwindow list.
