# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/Makefile

This is the historical cross-platform makefile for the `ipsend`, `ipresend`, and `iptest` packet-generation utilities.

It defines common object groups for IP language parsing, packet sending, resend, tests, and platform-specific device backends: BPF, NIT, DLPI/Solaris, BSD, Linux, Ultrix, HP-UX, and SunOS variants. The default `all` target prints available platform targets rather than building.

Targets generate parser/lexer objects from `iplang`, create compatibility symlinks to `iplang`, `netinet`, and `ipf`, and link the three programs with platform-specific libraries and flags. It also provides explicit rules for vendored IPFilter helper objects and a clean target.

This file is not the active FreeBSD bsd.prog.mk makefile for each utility; it is portable upstream build glue retained in the source tree.
