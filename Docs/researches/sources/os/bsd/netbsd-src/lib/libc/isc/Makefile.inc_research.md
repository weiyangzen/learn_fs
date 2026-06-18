# File Research: sources/os/bsd/netbsd-src/lib/libc/isc/Makefile.inc

Build fragment for imported ISC support code.

Adds:
- Path `${.CURDIR}/isc`.
- Sources `assertions.c`, `ev_timers.c`, and `ev_streams.c`.

These support resolver/eventlib functionality inside libc.
