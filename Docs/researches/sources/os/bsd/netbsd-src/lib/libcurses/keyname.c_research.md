# File Research: sources/os/bsd/netbsd-src/lib/libcurses/keyname.c

Implements key-code name formatting: `keyname(int key)` and wide `key_name(wchar_t key)`.

`keyname` uses a static buffer to format control, printable, delete, meta, function, and `KEY_*` values in sync with `curses.h`, falling back to `UNKNOWN KEY`. `key_name` delegates to `keyname` and strips the `M-` prefix for wide builds. The static buffer makes returned names transient and non-reentrant.
