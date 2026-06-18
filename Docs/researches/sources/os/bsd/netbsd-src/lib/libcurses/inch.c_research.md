# File Research: sources/os/bsd/netbsd-src/lib/libcurses/inch.c

Implements narrow `chtype` cell extraction: `inch`, `mvinch`, `mvwinch`, and `winch`.

`winch` returns the current cell character masked with `__CHARTEXT` plus user-visible attributes masked with `__ATTRIBUTES`. When color is active, default-color bits are stripped before returning so callers do not see internal default-color encoding.
