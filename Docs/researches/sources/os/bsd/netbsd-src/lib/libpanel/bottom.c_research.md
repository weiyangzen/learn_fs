# File Research: sources/os/bsd/netbsd-src/lib/libpanel/bottom.c

Read completely: 48 lines.

`bottom_panel` moves a visible panel to the bottom of the user-visible deck, just above the phantom `stdscr` panel. It rejects null and hidden panels, hides the panel to remove it from its current position, then reinserts it after `_stdscr_panel`.

Security/reliability notes: relies on `_stdscr_panel` being present, which is established when the first real panel is created.
