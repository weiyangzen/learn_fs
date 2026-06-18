# File Research: sources/os/bsd/netbsd-src/lib/libcurses/curs_set.c

Read completely: 101 lines.

This file implements cursor visibility control. `curs_set(0)`, `curs_set(1)`, and `curs_set(2)` map to `cursor_invisible`, `cursor_normal`, and `cursor_visible` terminfo capabilities respectively. On success it emits the sequence, flushes the screen output file, stores the new mode in `_cursesi_screen->old_mode`, and returns the previous mode. `__restore_cursor_vis` reapplies the stored mode.

Important interactions: depends on `_cursesi_screen`, terminfo cursor-visibility capabilities, `tputs`, and `__cputchar`.

Reliability notes: unsupported visibility requests return `ERR`. The name `old_mode` stores current/last requested visibility after success, not just a historical value.
