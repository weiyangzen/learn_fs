# File Research: sources/os/bsd/netbsd-src/lib/libcurses/scanw.c

Implements formatted input APIs: `scanw`, `wscanw`, movement variants, `vw_scanw`, and alias `vwscanw`.

`vw_scanw` reads up to 1024 bytes with `wgetnstr`, then parses with `vsscanf`, returning `OK` only if at least one conversion succeeds. The `mvwscanw` implementation calls `move(y, x)` rather than `wmove(win, y, x)`, so its movement target is `stdscr` before scanning the supplied window.
