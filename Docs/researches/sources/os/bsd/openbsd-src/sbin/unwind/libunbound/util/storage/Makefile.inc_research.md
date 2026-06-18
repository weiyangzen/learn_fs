# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/Makefile.inc

OpenBSD make include for the `libunbound/util/storage` subdirectory.

Build behavior:
- Adds `.PATH` for `${.CURDIR}/libunbound/util/storage`.
- Adds storage utility sources to `SRCS`: `dnstree.c`, `lookup3.c`, `lruhash.c`, and `slabhash.c`.

Role:
- Wires the storage support modules into the OpenBSD `sbin/unwind` build of libunbound.
