# File Research: sources/os/bsd/netbsd-src/lib/libcurses/echo_wchar.c

Read completely: 85 lines.

This file implements wide-character echo helpers: `echo_wchar`, `wecho_wchar`, and `pecho_wchar`. They add a `cchar_t` to a window with `wadd_wch` and then refresh either the window (`wrefresh`) or pad (`prefresh` with saved pad coordinates).

Important interactions: pad refresh uses `pad->pbegy`, `pbegx`, `sbegy`, `sbegx`, `smaxy`, and `smaxx`.

Reliability notes: `pecho_wchar` assumes `pad` is valid before reading saved pad coordinates after `wadd_wch` succeeds.
