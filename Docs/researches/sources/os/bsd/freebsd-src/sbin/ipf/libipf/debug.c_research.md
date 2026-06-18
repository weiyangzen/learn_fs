# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/debug.c

This file implements debug printing helpers.

`debuglevel` is global. `debug()` prints a formatted message to stderr when `debuglevel > 0` and the message level is within range. `ipfkdebug()` attempts to print when global `opts` has `OPT_DEBUG`.

Implementation note: `ipfkdebug()` passes a `va_list` to `debug()` as a normal variadic argument, which is not a correct forwarding pattern; it may not print intended arguments correctly.
