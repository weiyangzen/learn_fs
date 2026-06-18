# File Research: sources/os/bsd/netbsd-src/lib/libpanel/replace.c

Read completely: 53 lines.

`replace_panel` changes the curses window associated with a panel. For visible panels, it touches overlap regions for the old window before replacing it, so exposed regions are refreshed.

It rejects null panel or null window and returns `OK` on success.

Security/reliability notes: ownership of old and new `WINDOW *` remains with the caller.
