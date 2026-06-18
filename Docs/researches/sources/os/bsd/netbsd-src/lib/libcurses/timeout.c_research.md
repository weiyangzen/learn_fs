# File Research: sources/os/bsd/netbsd-src/lib/libcurses/timeout.c

Implements input timeout controls: `timeout` and `wtimeout`.

`wtimeout` maps negative delays to blocking mode (`-1`), zero to nonblocking, and positive millisecond delays to decisecond `VTIME` units, capped at 255. `timeout` applies the same setting to `stdscr`.
