# File Research: sources/os/bsd/netbsd-src/lib/libpanel/new.c

Read completely: 76 lines.

`new_panel` creates a visible panel for a non-null, non-`stdscr` curses window. On first use it initializes the phantom `_stdscr_panel` with current `stdscr` and inserts it at the bottom of the deck, then allocates and inserts the new panel at the top.

The internal `_new_panel` initializes `win`, sets `user` null, and links into the deck.

Security/reliability notes: panel allocation failure returns null. The phantom panel tracks `stdscr` only when the deck is first initialized.
