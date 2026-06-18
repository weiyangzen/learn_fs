# File Research: sources/os/bsd/netbsd-src/lib/libpanel/del.c

Read completely: 63 lines.

`del_panel` hides a panel, frees its `PANEL` object, and, if the last remaining panel is the phantom `stdscr` panel, hides that too and asserts the deck is empty.

It does not delete or free the associated curses `WINDOW`.

Security/reliability notes: callers must not use the `PANEL *` after deletion. The associated window lifetime remains the caller’s responsibility.
