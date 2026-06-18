# File Research: sources/os/bsd/netbsd-src/lib/libcurses/fullname.c

Read completely: 64 lines.

This file implements `fullname(const char *bp, char *def)`, extracting the terminal's full name from a termcap-style alias string. It repeatedly copies alias text up to `|` or `:` into `def`, so the final copied alias before `:` is returned. `def` is initialized to an empty string first.

Important interactions: used with terminal description strings where aliases are pipe-separated and the description begins after `:`.

Reliability notes: there is no destination size parameter, so callers must provide a large enough `def` buffer.
