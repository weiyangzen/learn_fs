# File Research: sources/os/bsd/netbsd-src/lib/libcurses/echochar.c

Read completely: 83 lines.

This file implements narrow echo helpers: `echochar`, `wechochar`, and `pechochar`. They add a `chtype` through `waddch` and refresh the target window or pad.

Important interactions: `echochar` may be a macro unless `_CURSES_USE_MACROS` is disabled. `pechochar` uses saved pad refresh coordinates exactly like the wide version.

Reliability notes: pad coordinate dereferences occur after `waddch` succeeds, so callers must pass a valid pad/window.
