# File Research: sources/os/bsd/netbsd-src/lib/libpanel/update.c

Read completely: 62 lines.

`update_panels` propagates refresh state through the deck and then calls `wnoutrefresh` from bottom to top. For each panel, it touches overlaps in every panel above it so higher panels repaint over lower ones.

Security/reliability notes: this function updates curses virtual screen state; callers still need the normal curses refresh/doupdate flow to display changes.
