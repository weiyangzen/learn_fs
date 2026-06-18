# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/Makefile.inc

`util/data/Makefile.inc` is the OpenBSD make include for the bundled libunbound data utilities used by `unwind`. It adds `${.CURDIR}/libunbound/util/data` to `.PATH` and appends the data-layer source files to `SRCS`.

The selected files are `dname.c`, `msgencode.c`, `msgparse.c`, `msgreply.c`, and `packed_rrset.c`. This make fragment therefore pulls in domain-name handling, DNS message parsing/encoding, reply structures, and packed RRset support for the local libunbound build.
