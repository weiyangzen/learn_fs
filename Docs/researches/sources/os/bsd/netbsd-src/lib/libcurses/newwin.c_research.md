# File Research: sources/os/bsd/netbsd-src/lib/libcurses/newwin.c

Implements window, pad, subwindow, and derived-window allocation.

Public APIs include `newwin`, `newpad`, `subwin`, `derwin`, `subpad`, `dupwin`, and `is_pad`. Internals allocate line arrays, line metadata, contiguous cell storage for parent windows, screen winlist entries, subwindow line aliases, background defaults, dirty markers for pads, and geometry flags (`__ENDLINE`, `__FULLWIN`, `__SCROLLWIN`). `__set_subwin` maps child lines into parent cell storage, while `__swflags` derives terminal-sensitive refresh flags.
