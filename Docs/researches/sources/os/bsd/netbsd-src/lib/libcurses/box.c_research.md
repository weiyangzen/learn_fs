# File Research: sources/os/bsd/netbsd-src/lib/libcurses/box.c

Read completely: 63 lines.

This is a thin border convenience wrapper. `box(win, vert, hor)` calls `wborder` with the same vertical character for left/right, the same horizontal character for top/bottom, and zero corner arguments so `wborder` supplies defaults. `box_set` is the wide-character equivalent and calls `wborder_set` with null corners.

Non-wide builds return `ERR` from `box_set`.

Important interactions: all drawing behavior and validation are delegated to `border.c`.

Reliability notes: no additional checks beyond those in `wborder` and `wborder_set`.
