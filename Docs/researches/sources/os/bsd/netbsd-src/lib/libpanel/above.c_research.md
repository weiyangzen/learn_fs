# File Research: sources/os/bsd/netbsd-src/lib/libpanel/above.c

Read completely: 49 lines.

`panel_above` returns the visible panel above a given panel. With a null argument, it returns the bottom user-visible panel by asking for the panel above the phantom `stdscr` panel, or null if the deck is empty.

It returns null for hidden panels.

Security/reliability notes: callers must not pass stale/freed `PANEL *` values; hidden detection depends on internal TAILQ link state.
