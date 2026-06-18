# File Research: sources/os/bsd/openbsd-src/sbin/unwind/Makefile

Builds the `unwind` DNS resolver daemon.

Key settings:
- `PROG=unwind`
- Sources include `control.c`, `resolver.c`, `frontend.c`, `log.c`, `unwind.c`, parser, config printing, and DNS64 synthesis.
- Includes bundled `libunbound/Makefile.inc`.
- Adds warning flags and include paths.
- Links `-levent -lutil -lssl -lcrypto`.
- Sets `LDSTATIC=` so unwind is not built static by default.

Role:
- Daemon build file with libevent, OpenSSL, libutil, and embedded unbound integration.
