# File Research: sources/os/bsd/netbsd-src/lib/libcurses/getyx.c

Read completely: 160 lines.

This file implements coordinate accessor functions backing public macros: `getpary`, `getparx`, `getcury`, `getcurx`, `getbegy`, `getbegx`, `getmaxy`, and `getmaxx`.

Parent-relative accessors return `-1` if the window is null or not a subwindow. Other accessors return `ERR` for null windows and otherwise return the requested field from `WINDOW`.

Important interactions: `curses.h` macros `getyx`, `getbegyx`, `getmaxyx`, and `getparyx` call these functions to fill caller variables.

Reliability notes: because `ERR` is also `-1`, null-window errors and valid parent-query “not a subwindow” results are intentionally indistinguishable for parent accessors.
