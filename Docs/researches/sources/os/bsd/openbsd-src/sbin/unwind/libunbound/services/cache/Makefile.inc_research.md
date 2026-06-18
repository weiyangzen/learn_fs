# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/Makefile.inc

OpenBSD make fragment for libunbound cache services.

Contents:
- Adds `${.CURDIR}/libunbound/services/cache` to `.PATH`.
- Adds `dns.c`, `infra.c`, and `rrset.c` to `SRCS`.

Role:
- Includes DNS message cache, infrastructure cache, and RRset cache implementations in the unwind/libunbound build.
