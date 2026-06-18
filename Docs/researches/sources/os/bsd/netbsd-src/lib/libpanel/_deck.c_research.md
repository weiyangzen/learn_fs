# File Research: sources/os/bsd/netbsd-src/lib/libpanel/_deck.c

Read completely: 34 lines.

This defines the hidden global panel deck `_deck` as a TAILQ initialized empty, and the hidden phantom `_stdscr_panel`.

These globals back all libpanel Z-order operations.

Security/reliability notes: global state means libpanel operations are not independently namespaced per screen or thread.
