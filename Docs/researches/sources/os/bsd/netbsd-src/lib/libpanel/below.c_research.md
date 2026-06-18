# File Research: sources/os/bsd/netbsd-src/lib/libpanel/below.c

Read completely: 50 lines.

`panel_below` returns the panel below a given visible panel. With a null argument, it returns the top panel. It hides the phantom `stdscr` panel from callers by returning null when that would be the result.

Security/reliability notes: same stale-pointer caveat as other panel list helpers.
