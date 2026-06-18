# File Research: sources/os/bsd/netbsd-src/lib/libpanel/window.c

Read completely: 42 lines.

`panel_window` returns the curses window associated with a panel, or null for a null panel.

Security/reliability notes: returned pointer is borrowed; caller must not free or mutate it in ways that bypass panel bookkeeping for movement/replacement.
