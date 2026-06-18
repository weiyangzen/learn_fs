# File Research: sources/os/bsd/openbsd-src/sbin/Makefile.inc

Common make include for OpenBSD `sbin` programs.

It defaults `BINDIR` to `/sbin`, propagates `${STATIC}` into `LDSTATIC`, and enables `-Werror-implicit-function-declaration` across these utility builds.
