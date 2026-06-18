# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/Makefile.inc

`sldns/Makefile.inc` is the OpenBSD make include for building the bundled `sldns` subset used by `unwind`'s libunbound copy. It adds `${.CURDIR}/libunbound/sldns` to `.PATH` and appends the selected resolver parsing/formatting sources to `SRCS`: `keyraw.c`, `parseutil.c`, `rrdef.c`, `sbuffer.c`, `sldns_parse.c`, `str2wire.c`, and `wire2str.c`.

The file creates `sldns_parse.c` as a build-time symlink to `libunbound/sldns/parse.c`, then lists that symlink in `CLEANFILES`. This avoids compiling a source file named exactly `parse.c` through the OpenBSD build while still using the upstream parser implementation.
