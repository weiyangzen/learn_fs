# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/Makefile

This Makefile builds the OpenBSD `slaacd` daemon.

Key settings:
- `PROG=slaacd`
- `SRCS=control.c engine.c frontend.c log.c slaacd.c`
- `MAN=slaacd.8`
- Adds warning-heavy `CFLAGS` and includes `${.CURDIR}`.
- Links with `-levent -lutil`.
- Sets `LDSTATIC=` so `slaacd` is not static by default.

Integration:
- `control.c` is one component of a multi-process/libevent daemon with frontend and engine processes.

Risk notes:
- Warning flags indicate the codebase expects strict prototype/declaration hygiene.
