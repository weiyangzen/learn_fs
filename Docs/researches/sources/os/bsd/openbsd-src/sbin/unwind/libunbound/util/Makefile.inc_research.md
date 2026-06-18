# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/Makefile.inc

`Makefile.inc` adds libunbound utility sources to the OpenBSD `unwind` build. It sets `.PATH` to `libunbound/util` and appends allocator, config parser/lexer, EDNS, locks, event, module, networking, proxy protocol, randomness, tree, regional allocation, RTT, siphash, TCP limit, timing, tube, event plugin, logging, and winsock event sources.

Because this subtree already has another `log.c` naming context, it builds `util_log.c` by symlinking `${.CURDIR}/libunbound/util/log.c` and registers that generated symlink in `CLEANFILES`.
